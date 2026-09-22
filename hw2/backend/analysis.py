import json
import re
from collections import Counter
from itertools import combinations
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "data_cvpr2024.json"
TOPIC_LIMIT = 10
NETWORK_NODE_LIMIT = 100

STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "based",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "this",
    "through",
    "to",
    "toward",
    "towards",
    "under",
    "using",
    "via",
    "with",
    "without",
}

TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def load_papers():
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def extract_title_keywords(title):
    tokens = TOKEN_PATTERN.findall(title.lower())

    return {
        token
        for token in tokens
        if token not in STOP_WORDS
        and len(token) >= 2
        and not token.isdigit()
    }


def get_top_topics(limit=TOPIC_LIMIT):
    keyword_counts = Counter()

    for paper in load_papers():
        title = paper.get("title", "")
        keyword_counts.update(extract_title_keywords(title))

    topics = [
        {
            "keyword": keyword,
            "count": count,
        }
        for keyword, count in sorted(
            keyword_counts.items(),
            key=lambda item: (-item[1], item[0]),
        )[:limit]
    ]

    return topics


def get_keyword_network():
    keyword_counts = Counter()
    pair_counts = Counter()

    for paper in load_papers():
        title = paper.get("title", "")
        keywords = sorted(extract_title_keywords(title))

        keyword_counts.update(keywords)
        pair_counts.update(combinations(keywords, 2))


    top_keywords = {
        keyword
        for keyword, count in sorted(
            keyword_counts.items(),
            key=lambda item: (-item[1], item[0]),
        )[:NETWORK_NODE_LIMIT]
    }


    nodes = [
        {
            "id": keyword,
            "count": keyword_counts[keyword],
        }
        for keyword in sorted(top_keywords)
    ]


    links = [
        {
            "source": source,
            "target": target,
            "value": count,
        }
        for (source, target), count in sorted(
            pair_counts.items(),
            key=lambda item: (-item[1], item[0][0], item[0][1]),
        )
        if source in top_keywords
        and target in top_keywords
    ]


    return {
        "nodes": nodes,
        "links": links,
    }