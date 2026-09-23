import json
import re
import time
from collections import Counter
from pathlib import Path

import requests
from bs4 import BeautifulSoup


PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = PROJECT_ROOT / "data" / "trend_data.json"

CONFERENCES = {
    "CVPR": [2022, 2023, 2024],
    "ICCV": [2023],
    "ECCV": [2022, 2024],
}

BASE_URL = "https://openaccess.thecvf.com"
REQUEST_TIMEOUT = 20
REQUEST_DELAY = 1.0

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

TOKEN_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)?")


def extract_title_keywords(title):
    tokens = TOKEN_PATTERN.findall(title.lower())

    return {
        token
        for token in tokens
        if token not in STOP_WORDS
        and len(token) >= 2
        and not token.isdigit()
    }


def build_conference_url(conference, year):
    return f"{BASE_URL}/{conference}{year}?day=all"


def fetch_paper_titles(session, conference, year):
    url = build_conference_url(conference, year)

    print(f"[爬取] {conference} {year}: {url}")

    response = session.get(
        url,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    titles = []

    for link in soup.find_all("a"):
        href = str(link.get("href") or "")

        if (
            f"/{conference}{year}/html/" in href
            and "_paper.html" in href
        ):
            title = link.get_text(" ", strip=True)

            if title:
                titles.append(title)

    unique_titles = list(dict.fromkeys(titles))

    print(
        f"[完成] {conference} {year}: "
        f"取得 {len(unique_titles)} 篇論文"
    )

    return unique_titles


def build_trend_data():
    trend_rows = []

    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "ConferenceTrendStatistics/1.0 "
            "(educational project)"
        )
    })

    for conference, years in CONFERENCES.items():
        for year in years:
            try:
                titles = fetch_paper_titles(
                    session,
                    conference,
                    year,
                )

                keyword_counts = Counter()

                for title in titles:
                    keywords = extract_title_keywords(title)
                    keyword_counts.update(keywords)

                for keyword, count in sorted(
                    keyword_counts.items(),
                    key=lambda item: (-item[1], item[0]),
                ):
                    trend_rows.append({
                        "year": year,
                        "conference": conference,
                        "keyword": keyword,
                        "count": count,
                    })

            except requests.RequestException as error:
                print(
                    f"[錯誤] {conference} {year} "
                    f"資料取得失敗：{error}"
                )

            time.sleep(REQUEST_DELAY)

    return trend_rows


def main():
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    trend_data = build_trend_data()

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            trend_data,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print()
    print(f"[完成] 已輸出 {len(trend_data)} 筆熱度統計")
    print(f"[檔案] {OUTPUT_FILE}")


if __name__ == "__main__":
    main()