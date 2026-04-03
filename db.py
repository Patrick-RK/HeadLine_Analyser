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
           (scrape_run_id, text, position, compound, neg, neu, pos, overall_sentiment)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
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
