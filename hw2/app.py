"""Flask application for the conference hot-term statistics platform."""

from pathlib import Path
import sqlite3

from flask import Flask, jsonify, request, send_from_directory


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "data" / "conference_terms.db"
FRONTEND_DIR = BASE_DIR / "frontend"

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")


def get_db_connection():
    """Open a SQLite connection with dictionary-like rows."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/api/terms")
def list_terms():
    """Return hot terms ordered by frequency, with optional search filtering."""
    keyword = request.args.get("q", "").strip()
    connection = get_db_connection()
    try:
        rows = connection.execute(
            """
            SELECT term, category, frequency, trend, updated_at
            FROM hot_terms
            WHERE term LIKE ? OR category LIKE ?
            ORDER BY frequency DESC, term ASC
            """,
            (f"%{keyword}%", f"%{keyword}%"),
        ).fetchall()
        return jsonify([dict(row) for row in rows])
    finally:
        connection.close()


if __name__ == "__main__":
    app.run(debug=True)
