"""Create and seed the local SQLite database."""

from pathlib import Path
import sqlite3


BASE_DIR = Path(__file__).resolve().parents[1]
DATABASE_PATH = BASE_DIR / "data" / "conference_terms.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

SEED_TERMS = [
    ("Large Language Model", "AI", 982, "up"),
    ("RAG", "AI", 841, "up"),
    ("Transformer", "Machine Learning", 798, "stable"),
    ("Diffusion Model", "Computer Vision", 672, "up"),
    ("Federated Learning", "Security", 514, "down"),
]


def initialize_database():
    """Create tables and insert sample terms without duplicating existing data."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        connection.executemany(
            """
            INSERT INTO hot_terms (term, category, frequency, trend)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(term) DO NOTHING
            """,
            SEED_TERMS,
        )


if __name__ == "__main__":
    initialize_database()
    print(f"Database initialized: {DATABASE_PATH}")
