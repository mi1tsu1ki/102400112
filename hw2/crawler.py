"""DBLP 論文資料獲取與 SQLite 持久化模組。

模組引入建議：
    1. requests：負責呼叫 DBLP 公開 HTTP API。
    2. sqlite3：Python 標準函式庫，負責嵌入式 SQLite 資料庫。
    3. time：在 API 請求之間加入延遲，降低過於頻繁請求的風險。

使用範例：
    python crawler.py

    或在其他 Python 程式中：
        papers = fetch_conference_papers("CVPR", [2023, 2024])
        save_papers_to_db(papers)
"""

from __future__ import annotations

from pathlib import Path
import sqlite3
import time
from typing import Any

import requests


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "data" / "conference_terms.db"
DBLP_API_URL = "https://dblp.org/search/publ/api"
DEFAULT_PAGE_SIZE = 100
DEFAULT_REQUEST_DELAY = 1.0
REQUEST_TIMEOUT = 20
MAX_RETRIES = 3
RETRY_DELAY = 2.0


def _create_papers_table(connection: sqlite3.Connection) -> None:
    """建立論文資料表；可安全地對既有資料庫重複執行。"""
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            abstract TEXT NOT NULL DEFAULT '',
            authors TEXT NOT NULL DEFAULT '',
            year INTEGER,
            ee TEXT NOT NULL DEFAULT '',
            venue TEXT NOT NULL DEFAULT '',
            UNIQUE(title, year, venue)
        )
        """
    )


def _as_text(value: Any) -> str:
    """將 DBLP 回傳的字串或空值統一轉成可存入資料庫的文字。"""
    if value is None:
        return ""
    return str(value).strip()


def _parse_authors(author_data: Any) -> str:
    """解析 DBLP 的作者欄位；DBLP 可能回傳單一 dict 或 dict 陣列。"""
    if not author_data:
        return ""
    authors = author_data if isinstance(author_data, list) else [author_data]
    names = []
    for author in authors:
        if isinstance(author, dict):
            name = _as_text(author.get("text") or author.get("name"))
        else:
            name = _as_text(author)
        if name:
            names.append(name)
    return ", ".join(names)


def _parse_hit(hit: dict[str, Any], venue: str = "") -> dict[str, Any]:
    """把 DBLP 單筆 hit 轉成平台統一的論文資料格式。"""
    info = hit.get("info", hit)
    authors_data = info.get("authors", {})
    author_data = (
        authors_data.get("author", [])
        if isinstance(authors_data, dict)
        else authors_data
    )
    return {
        "title": _as_text(info.get("title")),
        # DBLP 搜尋 API 不一定提供 abstract，因此缺少時明確存成空字串。
        "abstract": _as_text(info.get("abstract")),
        "authors": _parse_authors(author_data),
        "year": int(info["year"]) if _as_text(info.get("year")).isdigit() else None,
        "ee": _as_text(info.get("ee")),
        "venue": _as_text(info.get("venue")) or venue,
    }


def _request_page(
    query: str,
    offset: int,
    page_size: int,
    session: requests.Session,
) -> dict[str, Any]:
    """請求 DBLP 單頁資料；失敗時重試，最終以空字典安全結束。

    MAX_RETRIES 代表第一次請求失敗後的重試次數，因此最多會執行
    1 次初始請求加上 3 次重試。HTTP 錯誤、連線錯誤、逾時與 JSON
    格式錯誤都會進入相同的重試流程。
    """
    params = {"q": query, "format": "json", "h": page_size, "f": offset}
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = session.get(
                DBLP_API_URL,
                params=params,
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                raise ValueError("DBLP API 回傳格式不是 JSON 物件")
            return payload
        except (requests.RequestException, ValueError) as error:
            attempt_number = attempt + 1
            if attempt < MAX_RETRIES:
                print(
                    f"[WARN] DBLP API 請求失敗（第 {attempt_number} 次）："
                    f"{error}；{RETRY_DELAY:g} 秒後重試。"
                )
                time.sleep(RETRY_DELAY)
            else:
                print(
                    f"[ERROR] DBLP API 請求重試 {MAX_RETRIES} 次後仍失敗："
                    f"{error}"
                )
    return {}


def search_paper_exact(
    title: str,
    *,
    request_delay: float = DEFAULT_REQUEST_DELAY,
    session: requests.Session | None = None,
) -> dict[str, Any] | None:
    """依單一論文題目精確查詢，找不到完全相符的題目時回傳 None。

    DBLP 的搜尋結果可能包含相似標題，因此除了在 API 中使用引號查詢，
    仍會在本地以去除首尾空白並忽略大小寫的方式做一次精確比對。
    """
    normalized_title = title.strip().casefold()
    if not normalized_title:
        raise ValueError("論文題目不可為空白")

    client = session or requests.Session()
    payload = _request_page(f'"{title.strip()}"', 0, DEFAULT_PAGE_SIZE, client)
    result = payload.get("result", {})
    hits_data = result.get("hits", {}) if isinstance(result, dict) else {}
    hits = hits_data.get("hit", []) if isinstance(hits_data, dict) else []
    if isinstance(hits, dict):
        hits = [hits]
    for hit in hits:
        paper = _parse_hit(hit)
        if paper["title"].strip().casefold() == normalized_title:
            return paper
    if request_delay > 0:
        time.sleep(request_delay)
    return None


def fetch_conference_papers(
    conference: str,
    years: int | list[int],
    *,
    page_size: int = DEFAULT_PAGE_SIZE,
    request_delay: float = DEFAULT_REQUEST_DELAY,
    session: requests.Session | None = None,
) -> list[dict[str, Any]]:
    """依會議名稱和年份批量抓取論文，直到 DBLP 分頁資料全部讀完。

    `years` 可傳入單一年份或年份清單；conference 建議使用 CVPR、ICCV、
    ECCV 等 DBLP venue 名稱。每頁使用 offset + page_size 前進，並依
    `hits@total` 判斷是否已經取得全部結果。
    """
    if not conference.strip():
        raise ValueError("會議名稱不可為空白")
    selected_years = [years] if isinstance(years, int) else list(years)
    if not selected_years:
        raise ValueError("至少需要一個年份")
    if page_size <= 0:
        raise ValueError("page_size 必須大於 0")

    client = session or requests.Session()
    papers: list[dict[str, Any]] = []
    for year in selected_years:
        query = f"venue:{conference.strip()} year:{year}"
        offset = 0
        total = None
        while total is None or offset < total:
            payload = _request_page(query, offset, page_size, client)
            result = payload.get("result", {})
            if not isinstance(result, dict):
                print("[ERROR] DBLP API 回傳缺少有效的 result，停止目前年份抓取。")
                break
            hits_data = result.get("hits", {})
            if not isinstance(hits_data, dict):
                print("[ERROR] DBLP API 回傳缺少有效的 hits，停止目前年份抓取。")
                break
            hits = hits_data.get("hit", [])
            if isinstance(hits, dict):
                hits = [hits]
            total_value = hits_data.get("@total")
            total = int(total_value) if _as_text(total_value).isdigit() else 0
            papers.extend(_parse_hit(hit, conference.strip()) for hit in hits)
            if not hits:
                break
            offset += len(hits)
            if offset < total and request_delay > 0:
                time.sleep(request_delay)
    return papers


def save_papers_to_db(
    papers: list[dict[str, Any]],
    database_path: Path | str = DATABASE_PATH,
) -> int:
    """將論文寫入 SQLite；相同的題目、年份、會議會更新而不重複插入。

    回傳實際處理的資料筆數，方便呼叫端在批量工作後記錄結果。
    """
    target = Path(database_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(target)
    try:
        _create_papers_table(connection)
        with connection:
            connection.executemany(
                """
                INSERT INTO papers (title, abstract, authors, year, ee, venue)
                VALUES (:title, :abstract, :authors, :year, :ee, :venue)
                ON CONFLICT(title, year, venue) DO UPDATE SET
                    abstract = excluded.abstract,
                    authors = excluded.authors,
                    ee = excluded.ee
                """,
                papers,
            )
        return len(papers)
    finally:
        connection.close()


if __name__ == "__main__":
    # 範例：抓取近三年資料。正式批次作業可改成命令列參數或排程工作。
    collected_papers = fetch_conference_papers("CVPR", [2022, 2023, 2024])
    saved_count = save_papers_to_db(collected_papers)
    print(f"抓取 {len(collected_papers)} 篇，寫入資料庫 {saved_count} 筆。")
