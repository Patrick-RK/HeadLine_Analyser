import json
import os
import secrets
from functools import wraps

from flask import Flask, jsonify, redirect, url_for, render_template, flash, request

from config import SITES
from db import (
    init_db, insert_scrape_run, insert_headlines,
    get_latest_run, get_run, get_headlines_for_run, get_all_runs,
    get_latest_run_per_site,
)
from utilities import (
    fetch_website, strip_html, add_reverse_column,
    headline_analyser, calculate_moving_averages, build_plotly_figure,
    find_cross_site_matches,
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "headline-analyser-dev-key")

API_KEY = os.environ.get("API_KEY", secrets.token_urlsafe(32))


# ── API key auth ──────────────────────────────────────────────

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = (
            request.headers.get("X-API-Key")
            or request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
        )
        if not key or not secrets.compare_digest(key, API_KEY):
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


# ── DB init ───────────────────────────────────────────────────

@app.before_request
def _init_db():
    if not getattr(app, "_db_initialised", False):
        init_db()
        app._db_initialised = True


# ── Web routes (no auth — served to browser) ─────────────────

@app.route("/")
def dashboard():
    threshold = request.args.get("threshold", 50, type=int)
    site_urls = [s["url"] for s in SITES.values()]
    runs_data = get_latest_run_per_site(site_urls)
    url_to_name = {s["url"]: s["name"] for s in SITES.values()}

    # Per-site sentiment summaries
    site_stats = []
    for rd in runs_data:
        headlines = rd["headlines"]
        if not headlines:
            continue
        compounds = [h["compound"] for h in headlines]
        pos = sum(1 for h in headlines if h["overall_sentiment"] == "Positive")
        neg = sum(1 for h in headlines if h["overall_sentiment"] == "Negative")
        neu = sum(1 for h in headlines if h["overall_sentiment"] == "Neutral")
        site_stats.append({
            "name": url_to_name.get(rd["url"], rd["url"]),
            "url": rd["url"],
            "run": rd["run"],
            "count": len(headlines),
            "avg_compound": sum(compounds) / len(compounds),
            "positive": pos,
            "negative": neg,
            "neutral": neu,
        })

    matches = find_cross_site_matches(runs_data, threshold=threshold) if len(runs_data) >= 2 else []

    # Leaderboard — most positive, most negative, most neutral
    leaders = {}
    if site_stats:
        leaders["positive"] = max(site_stats, key=lambda s: s["avg_compound"])
        leaders["negative"] = min(site_stats, key=lambda s: s["avg_compound"])
        leaders["neutral"] = min(site_stats, key=lambda s: abs(s["avg_compound"]))

    return render_template(
        "dashboard.html",
        site_stats=site_stats,
        matches=matches,
        url_to_name=url_to_name,
        threshold=threshold,
        sites=SITES,
        leaders=leaders,
    )


@app.route("/site/<path:site_url>")
def site_detail(site_url):
    site_urls = [s["url"] for s in SITES.values()]
    if site_url not in site_urls:
        flash("Unknown site.", "error")
        return redirect(url_for("dashboard"))

    runs_data = get_latest_run_per_site([site_url])
    if not runs_data:
        flash("No scrape data for this site yet.", "error")
        return redirect(url_for("dashboard"))

    rd = runs_data[0]
    url_to_name = {s["url"]: s["name"] for s in SITES.values()}
    return render_template(
        "site_detail.html",
        run=rd["run"],
        headlines=rd["headlines"],
        site_name=url_to_name.get(site_url, site_url),
    )


@app.route("/chart-data")
def chart_data_web():
    site_url = request.args.get("site_url")
    if not site_url:
        return jsonify({"data": [], "layout": {}})
    runs_data = get_latest_run_per_site([site_url])
    if not runs_data:
        return jsonify({"data": [], "layout": {}})
    records = runs_data[0]["headlines"]
    for r in records:
        if "text" in r and "headline" not in r:
            r["headline"] = r.pop("text")
    df = calculate_moving_averages(records)
    fig_json = build_plotly_figure(df)
    return fig_json, 200, {"Content-Type": "application/json"}


@app.route("/history")
def history():
    runs = get_all_runs()
    return render_template("history.html", runs=runs, sites=SITES)


# ── Web form routes (browser, no auth) ───────────────────────

@app.route("/scrape-all", methods=["POST"])
def scrape_all_form():
    total = 0
    errors = []

    for site_key, site in SITES.items():
        try:
            html = fetch_website(site["url"])
            titles = strip_html(
                html,
                selector=site["selector"],
                exclude_classes=site.get("exclude_classes"),
            )
            indexed = add_reverse_column(titles)

            if len(indexed) < 5:
                errors.append(f"{site['name']}: only {len(indexed)} headlines")
                continue

            results = headline_analyser(indexed)
            run_id = insert_scrape_run(site["url"], len(results))
            insert_headlines(run_id, results)
            total += len(results)
        except Exception as exc:
            errors.append(f"{site['name']}: {exc}")

    if total:
        flash(f"Scraped {total} headlines from {len(SITES) - len(errors)} sites.", "success")
    for err in errors:
        flash(err, "error")

    return redirect(url_for("dashboard"))


# ── Protected API routes (require X-API-Key) ─────────────────

@app.route("/api/scrape", methods=["POST"])
@require_api_key
def scrape():
    data = request.get_json(silent=True) or {}
    site_key = data.get("site", "rte")
    site = SITES.get(site_key)

    if not site:
        return jsonify({"error": f"Unknown site: {site_key}"}), 400

    try:
        html = fetch_website(site["url"])
        titles = strip_html(
            html,
            selector=site["selector"],
            exclude_classes=site.get("exclude_classes"),
        )
        indexed = add_reverse_column(titles)

        if len(indexed) < 5:
            return jsonify({"error": f"Only {len(indexed)} headlines found — too few to analyse"}), 422

        results = headline_analyser(indexed)
        run_id = insert_scrape_run(site["url"], len(results))
        insert_headlines(run_id, results)

        return jsonify({"run_id": run_id, "headline_count": len(results), "site": site["name"]})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/api/scrape-all", methods=["POST"])
@require_api_key
def scrape_all():
    total = 0
    errors = []
    runs = []

    for site_key, site in SITES.items():
        try:
            html = fetch_website(site["url"])
            titles = strip_html(
                html,
                selector=site["selector"],
                exclude_classes=site.get("exclude_classes"),
            )
            indexed = add_reverse_column(titles)

            if len(indexed) < 5:
                errors.append(f"{site['name']}: only {len(indexed)} headlines")
                continue

            results = headline_analyser(indexed)
            run_id = insert_scrape_run(site["url"], len(results))
            insert_headlines(run_id, results)
            total += len(results)
            runs.append({"run_id": run_id, "site": site["name"], "headline_count": len(results)})
        except Exception as exc:
            errors.append(f"{site['name']}: {exc}")

    return jsonify({"total_headlines": total, "runs": runs, "errors": errors})


@app.route("/api/chart-data")
@require_api_key
def chart_data():
    run_id = request.args.get("run_id", type=int)
    run = get_run(run_id) if run_id else get_latest_run()
    if not run:
        return jsonify({"data": [], "layout": {}})

    rows = get_headlines_for_run(run["id"])
    records = [dict(r) for r in rows]
    for r in records:
        r["headline"] = r.pop("text")
    df = calculate_moving_averages(records)
    fig_json = build_plotly_figure(df)
    return fig_json, 200, {"Content-Type": "application/json"}


@app.route("/api/runs")
@require_api_key
def api_runs():
    rows = get_all_runs()
    return jsonify([dict(r) for r in rows])


@app.route("/api/compare")
@require_api_key
def api_compare():
    threshold = request.args.get("threshold", 50, type=int)
    site_urls = [s["url"] for s in SITES.values()]
    runs_data = get_latest_run_per_site(site_urls)
    matches = find_cross_site_matches(runs_data, threshold=threshold)
    url_to_name = {s["url"]: s["name"] for s in SITES.values()}
    for group in matches:
        for m in group["matches"]:
            m["site_name"] = url_to_name.get(m["site"], m["site"])
    return jsonify({"threshold": threshold, "match_groups": matches})


@app.route("/api/runs/<int:run_id>/headlines")
@require_api_key
def api_headlines(run_id):
    run = get_run(run_id)
    if not run:
        return jsonify({"error": "Run not found"}), 404
    rows = get_headlines_for_run(run_id)
    return jsonify([dict(r) for r in rows])


if __name__ == "__main__":
    if not os.environ.get("API_KEY"):
        print(f"\n  ⚠  No API_KEY set — generated key: {API_KEY}\n")
    app.run(debug=True)
