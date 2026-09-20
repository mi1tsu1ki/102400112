CREATE TABLE IF NOT EXISTS hot_terms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    term TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    frequency INTEGER NOT NULL DEFAULT 0 CHECK (frequency >= 0),
    trend TEXT NOT NULL DEFAULT 'stable',
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_hot_terms_frequency
ON hot_terms (frequency DESC);
