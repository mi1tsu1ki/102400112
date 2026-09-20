"""論文摘要的熱門研究方向與關鍵詞圖譜分析。

模組引入建議：
    - jieba：中文斷詞工具，也能保留英文技術詞彙作為分析 token。
    - sqlite3、re、collections：皆為 Python 標準函式庫，分別用於
      讀取資料庫、排除標點及統計詞頻。
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations
from pathlib import Path
import re
import sqlite3
from typing import Any

import jieba


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "data" / "conference_terms.db"
TOPIC_LIMIT = 10

# 常見英文功能詞不具備研究方向的辨識力，先轉小寫再比對。
ENGLISH_STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "in", "into", "is", "it", "its", "of", "on", "or", "that", "the",
    "their", "this", "to", "was", "were", "with", "we", "which", "using",
    "use", "used", "based", "via", "can", "may", "more", "than", "also",
    "our", "these", "those", "have", "has", "had", "not", "but", "such",
}

# 英文技術詞、數字與中文詞保留；中間的 +、#、.、- 可保留 C++、C#、
# 3D、YOLO-v8 等電腦視覺常見術語。單獨的符號會被正規表示式排除。
TOKEN_PATTERN = re.compile(r"^[\u4e00-\u9fffA-Za-z0-9][\u4e00-\u9fffA-Za-z0-9.+#-]*$")


def _is_valid_token(token: str) -> bool:
    """判斷 token 是否為非停用詞且包含至少兩個有效字元。"""
    normalized = token.strip().lower()
    if len(normalized) <= 1 or normalized in ENGLISH_STOP_WORDS:
        return False
    return bool(TOKEN_PATTERN.fullmatch(normalized))


def tokenize_text(text: str) -> list[str]:
    """使用 jieba 斷詞，移除停用詞、標點與單字元 token。"""
    return [
        token.strip().lower()
        for token in jieba.lcut(text)
        if _is_valid_token(token)
    ]


def _load_documents(database_path: Path | str = DATABASE_PATH) -> list[str]:
    """讀取論文標題與摘要；資料表不存在時安全回傳空集合。"""
    connection = sqlite3.connect(database_path)
    try:
        table = connection.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name = 'papers'
            """
        ).fetchone()
        if table is None:
            return []
        rows = connection.execute(
            "SELECT title, abstract FROM papers"
        ).fetchall()
        return [
            f"{title or ''} {abstract or ''}"
            for title, abstract in rows
        ]
    finally:
        connection.close()


def analyze_hot_topics(
    database_path: Path | str = DATABASE_PATH,
    limit: int = TOPIC_LIMIT,
) -> list[dict[str, Any]]:
    """統計論文標題與摘要，回傳依詞頻排序的熱門研究方向。"""
    if limit <= 0:
        raise ValueError("limit 必須大於 0")
    counter = Counter(
        token
        for document in _load_documents(database_path)
        for token in tokenize_text(document)
    )
    return [
        {"keyword": keyword, "frequency": frequency}
        for keyword, frequency in counter.most_common(limit)
    ]


def build_keyword_graph(
    database_path: Path | str = DATABASE_PATH,
    limit: int = TOPIC_LIMIT,
) -> dict[str, list[dict[str, Any]]]:
    """建立 ECharts graph 所需的 nodes 與 links。

    連線代表兩個熱門詞曾出現在同一篇論文中，權重為共現論文數；
    節點大小則依詞頻線性映射，讓高頻研究方向更醒目。
    """
    topics = analyze_hot_topics(database_path, limit)
    keywords = {topic["keyword"] for topic in topics}
    frequencies = {topic["keyword"]: topic["frequency"] for topic in topics}
    documents = _load_documents(database_path)
    cooccurrence: Counter[tuple[str, str]] = Counter()

    for document in documents:
        document_keywords = sorted(
            keywords.intersection(tokenize_text(document))
        )
        cooccurrence.update(combinations(document_keywords, 2))

    max_frequency = max(frequencies.values(), default=1)
    nodes = [
        {
            "id": keyword,
            "name": keyword,
            "value": frequency,
            "symbolSize": 25 + 35 * frequency / max_frequency,
        }
        for keyword, frequency in frequencies.items()
    ]
    links = [
        {"source": source, "target": target, "value": weight}
        for (source, target), weight in cooccurrence.items()
    ]
    return {"nodes": nodes, "links": links}
