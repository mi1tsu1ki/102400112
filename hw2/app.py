"""Flask application for the conference hot-term statistics platform."""

from pathlib import Path
import sqlite3

from flask import Flask, jsonify, request, send_from_directory

from crawler import fetch_conference_papers, save_papers_to_db
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


@app.post("/api/crawl")
def crawl_papers():
    """Fetch and persist papers for one supported conference and year."""
    payload = request.get_json(silent=True) or {}
    conference = str(payload.get("conference", "")).strip().upper()
    year = payload.get("year")
    supported_conferences = {"CVPR", "ICCV", "ECCV"}

    if conference not in supported_conferences:
        return jsonify({"error": "conference 必須是 CVPR、ICCV 或 ECCV"}), 400
    try:
        year = int(year)
    except (TypeError, ValueError):
        return jsonify({"error": "year 必須是有效年份"}), 400
    if year < 1900 or year > 2100:
        return jsonify({"error": "year 必須介於 1900 到 2100"}), 400

    try:
        papers = fetch_conference_papers(conference, year)
        saved_count = save_papers_to_db(papers, DATABASE_PATH)
    except (OSError, TypeError, ValueError, sqlite3.Error) as error:
        app.logger.exception("Crawl failed for %s %s", conference, year)
        return jsonify({"error": f"爬取資料失敗：{error}"}), 500
    return jsonify({
        "conference": conference,
        "year": year,
        "fetched_count": len(papers),
        "saved_count": saved_count,
    })


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
