import json

from flask import Flask, redirect, url_for, render_template, flash, request

from config import SITES
from db import init_db, insert_scrape_run, insert_headlines, get_latest_run, get_run, get_headlines_for_run, get_all_runs
from utilities import fetch_website, strip_html, add_reverse_column, headline_analyser, calculate_moving_averages, build_plotly_figure

app = Flask(__name__)
app.secret_key = "headline-analyser-dev-key"


@app.before_request
def _init_db():
    """Initialise the database once on first request."""
    if not getattr(app, '_db_initialised', False):
        init_db()
        app._db_initialised = True


@app.route("/")
def dashboard():
    run_id = request.args.get("run_id", type=int)
    run = get_run(run_id) if run_id else get_latest_run()
    headlines = get_headlines_for_run(run["id"]) if run else []
    return render_template("dashboard.html", run=run, headlines=headlines, sites=SITES)


@app.route("/scrape", methods=["POST"])
def scrape():
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
def scrape_all():
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


@app.route("/api/chart-data")
def chart_data():
    run_id = request.args.get("run_id", type=int)
    run = get_run(run_id) if run_id else get_latest_run()
    if not run:
        return json.dumps({"data": [], "layout": {}}), 200, {"Content-Type": "application/json"}

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


if __name__ == "__main__":
    app.run(debug=True)
