import os
import sqlite3
from config import DATABASE


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")
    with open(schema_path) as f:
        conn.executescript(f.read())
    # Migrate existing DBs — add new model columns if missing
    existing = {row[1] for row in conn.execute("PRAGMA table_info(headlines)").fetchall()}
    for col, typ in [
        ("roberta_score", "REAL"), ("roberta_sentiment", "TEXT"),
        ("siebert_score", "REAL"), ("siebert_sentiment", "TEXT"),
        ("gpt_score", "REAL"), ("gpt_sentiment", "TEXT"),
    ]:
        if col not in existing:
            conn.execute(f"ALTER TABLE headlines ADD COLUMN {col} {typ}")
    conn.commit()
    conn.close()


def insert_scrape_run(url, headline_count):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO scrape_runs (url, headline_count) VALUES (?, ?)",
        (url, headline_count),
    )
    run_id = cur.lastrowid
    conn.commit()
    conn.close()
    return run_id


def insert_headlines(run_id, results):
    conn = get_db()
    conn.executemany(
        """INSERT INTO headlines
           (scrape_run_id, text, position, compound, neg, neu, pos, overall_sentiment,
            roberta_score, roberta_sentiment, siebert_score, siebert_sentiment,
            gpt_score, gpt_sentiment)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        [
            (
                run_id,
                r["headline"],
                r["position"],
                r["compound"],
                r["neg"],
                r["neu"],
                r["pos"],
                r["overall_sentiment"],
                r.get("roberta_score"),
                r.get("roberta_sentiment"),
                r.get("siebert_score"),
                r.get("siebert_sentiment"),
                r.get("gpt_score"),
                r.get("gpt_sentiment"),
            )
            for r in results
        ],
    )
    conn.commit()
    conn.close()


def get_latest_run():
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM scrape_runs ORDER BY scraped_at DESC LIMIT 1"
    ).fetchone()
    conn.close()
    return row


def get_run(run_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM scrape_runs WHERE id = ?", (run_id,)).fetchone()
    conn.close()
    return row


def get_headlines_for_run(run_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM headlines WHERE scrape_run_id = ? ORDER BY position DESC",
        (run_id,),
    ).fetchall()
    conn.close()
    return rows


def get_all_runs():
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM scrape_runs ORDER BY scraped_at DESC"
    ).fetchall()
    conn.close()
    return rows


def get_daily_sentiment(urls):
    """Return avg compound per site per day for the trends chart."""
    conn = get_db()
    placeholders = ",".join("?" for _ in urls)
    rows = conn.execute(
        f"""SELECT date(r.scraped_at) AS day, r.url,
                   AVG(h.compound) AS avg_compound,
                   COUNT(h.id) AS headline_count
            FROM scrape_runs r
            JOIN headlines h ON h.scrape_run_id = r.id
            WHERE r.url IN ({placeholders})
            GROUP BY day, r.url
            ORDER BY day""",
        urls,
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_latest_run_per_site(urls):
    """Return the most recent run for each URL, with its headlines."""
    conn = get_db()
    results = []
    for url in urls:
        run = conn.execute(
            "SELECT * FROM scrape_runs WHERE url = ? ORDER BY scraped_at DESC LIMIT 1",
            (url,),
        ).fetchone()
        if run:
            headlines = conn.execute(
                "SELECT * FROM headlines WHERE scrape_run_id = ? ORDER BY position DESC",
                (run["id"],),
            ).fetchall()
            results.append({
                "run": dict(run),
                "url": url,
                "headlines": [dict(h) for h in headlines],
            })
    conn.close()
    return results
