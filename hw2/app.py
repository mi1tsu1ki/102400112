"""Flask application for the conference hot-term statistics platform."""

from pathlib import Path
import sqlite3

from flask import Flask, jsonify, request, send_from_directory

from nlp_processor import analyze_hot_topics, build_keyword_graph


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


@app.get("/api/papers")
def list_papers():
    """Return crawled papers for the paper-management table."""
    connection = get_db_connection()
    try:
        table_exists = connection.execute(
            """
            SELECT 1 FROM sqlite_master
            WHERE type = 'table' AND name = 'papers'
            """
        ).fetchone()
        if table_exists is None:
            return jsonify([])
        rows = connection.execute(
            """
            SELECT title, year, authors, ee
            FROM papers
            ORDER BY year DESC, title ASC
            """
        ).fetchall()
        return jsonify([dict(row) for row in rows])
    finally:
        connection.close()


@app.get("/api/hot-topics")
def hot_topics():
    """回傳依詞頻排序的 Top 10 熱門研究方向。"""
    return jsonify(analyze_hot_topics(DATABASE_PATH))


@app.get("/api/keyword-graph")
def keyword_graph():
    """回傳 ECharts graph 使用的節點與共現連線。"""
    return jsonify(build_keyword_graph(DATABASE_PATH))


if __name__ == "__main__":
    app.run(debug=True)
