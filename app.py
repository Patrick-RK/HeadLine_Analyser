import json
import os
import secrets
from functools import wraps

from flask import Flask, jsonify, redirect, url_for, render_template, flash, request

from config import SITES
from db import (
    init_db, insert_scrape_run, insert_headlines,
    get_latest_run, get_run, get_headlines_for_run, get_all_runs,
)
from utilities import (
    fetch_website, strip_html, add_reverse_column,
    headline_analyser, calculate_moving_averages, build_plotly_figure,
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
    run_id = request.args.get("run_id", type=int)
    run = get_run(run_id) if run_id else get_latest_run()
    headlines = get_headlines_for_run(run["id"]) if run else []
    return render_template("dashboard.html", run=run, headlines=headlines, sites=SITES)


@app.route("/chart-data")
def chart_data_web():
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


@app.route("/history")
def history():
    runs = get_all_runs()
    return render_template("history.html", runs=runs, sites=SITES)


# ── Web form routes (browser, no auth) ───────────────────────

@app.route("/scrape", methods=["POST"])
def scrape_form():
    site_key = request.form.get("site", "rte")
    site = SITES.get(site_key)

    if not site:
        flash(f"Unknown site: {site_key}", "error")
        return redirect(url_for("dashboard"))

    try:
        html = fetch_website(site["url"])
        titles = strip_html(
            html,
            selector=site["selector"],
            exclude_classes=site.get("exclude_classes"),
        )
        indexed = add_reverse_column(titles)

        if len(indexed) < 5:
            flash(f"Only {len(indexed)} headlines found from {site['name']} — too few to analyse.", "error")
            return redirect(url_for("dashboard"))

        results = headline_analyser(indexed)
        run_id = insert_scrape_run(site["url"], len(results))
        insert_headlines(run_id, results)
        flash(f"Scraped {len(results)} headlines from {site['name']}.", "success")
    except Exception as exc:
        flash(f"Scrape of {site['name']} failed: {exc}", "error")

    return redirect(url_for("dashboard"))


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
