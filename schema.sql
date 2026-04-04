CREATE TABLE IF NOT EXISTS scrape_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scraped_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    url TEXT NOT NULL,
    headline_count INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS headlines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scrape_run_id INTEGER NOT NULL REFERENCES scrape_runs(id),
    text TEXT NOT NULL,
    position INTEGER NOT NULL,
    compound REAL NOT NULL,
    neg REAL NOT NULL,
    neu REAL NOT NULL,
    pos REAL NOT NULL,
    overall_sentiment TEXT NOT NULL,
    roberta_score REAL,
    roberta_sentiment TEXT,
    siebert_score REAL,
    siebert_sentiment TEXT,
    gpt_score REAL,
    gpt_sentiment TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_headlines_scrape_run ON headlines(scrape_run_id);
