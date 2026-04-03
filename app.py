import json
import os

from flask import Flask, redirect, url_for, render_template, flash, request
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

from config import SITES
from db import (
    init_db, insert_scrape_run, insert_headlines,
    get_latest_run, get_run, get_headlines_for_run, get_all_runs,
    create_user, get_user_by_username, get_user_by_id,
)
from utilities import (
    fetch_website, strip_html, add_reverse_column,
    headline_analyser, calculate_moving_averages, build_plotly_figure,
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "headline-analyser-dev-key")

bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "error"


# ── User model for Flask-Login ────────────────────────────────

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username


@login_manager.user_loader
def load_user(user_id):
    row = get_user_by_id(int(user_id))
    if row:
        return User(row["id"], row["username"])
    return None


# ── DB init ───────────────────────────────────────────────────

@app.before_request
def _init_db():
    if not getattr(app, "_db_initialised", False):
        init_db()
        app._db_initialised = True


# ── Auth routes ───────────────────────────────────────────────

@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "error")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return redirect(url_for("register"))

        if get_user_by_username(username):
            flash("Username already taken.", "error")
            return redirect(url_for("register"))

        pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        create_user(username, pw_hash)
        flash("Account created — please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        row = get_user_by_username(username)

        if row and bcrypt.check_password_hash(row["password_hash"], password):
            login_user(User(row["id"], row["username"]))
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard"))

        flash("Invalid username or password.", "error")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "success")
    return redirect(url_for("login"))


# ── Protected app routes ──────────────────────────────────────

@app.route("/")
@login_required
def dashboard():
    run_id = request.args.get("run_id", type=int)
    run = get_run(run_id) if run_id else get_latest_run()
    headlines = get_headlines_for_run(run["id"]) if run else []
    return render_template("dashboard.html", run=run, headlines=headlines, sites=SITES)


@app.route("/scrape", methods=["POST"])
@login_required
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
@login_required
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
@login_required
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
@login_required
def history():
    runs = get_all_runs()
    return render_template("history.html", runs=runs, sites=SITES)


if __name__ == "__main__":
    app.run(debug=True)
