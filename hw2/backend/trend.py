import json
from collections import Counter
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TREND_FILE = PROJECT_ROOT / "data" / "trend_data.json"
DEFAULT_TOP = 10
MAX_TOP = 30


def _load_rows():
    if not TREND_FILE.exists():
        return []

    with TREND_FILE.open("r", encoding="utf-8") as file:
        rows = json.load(file)

    if not isinstance(rows, list):
        raise ValueError("trend_data.json 必須是陣列")

    return rows


def get_trend_data(top=DEFAULT_TOP, conference=None):
    """Return a small, chart-ready trend response.

    The source is a long table, but the API aggregates it by
    ``conference/year/keyword`` and only returns the requested top keywords.
    This keeps the browser from creating one ECharts series per raw keyword.
    """
    if not isinstance(top, int) or not 1 <= top <= MAX_TOP:
        raise ValueError(f"top 必須介於 1 到 {MAX_TOP}")

    conference_filter = conference.strip().upper() if conference else None
    rows = []
    counts = Counter()

    for row in _load_rows():
        row_conference = str(row.get("conference", "")).upper()
        keyword = str(row.get("keyword", "")).strip()

        if not keyword or (conference_filter and row_conference != conference_filter):
            continue

        try:
            year = int(row["year"])
            count = int(row["count"])
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("trend_data.json 含有無效的 year 或 count") from error

        if count < 0:
            raise ValueError("trend_data.json 的 count 不可小於 0")

        normalized = {
            "year": year,
            "conference": row_conference,
            "keyword": keyword,
            "count": count,
        }
        rows.append(normalized)
        counts[keyword] += count

    keywords = [
        keyword
        for keyword, _ in sorted(
            counts.items(),
            key=lambda item: (-item[1], item[0]),
        )[:top]
    ]
    keyword_set = set(keywords)

    aggregated = Counter()
    for row in rows:
        if row["keyword"] in keyword_set:
            key = (row["conference"], row["year"], row["keyword"])
            aggregated[key] += row["count"]

    years = sorted({key[1] for key in aggregated})
    conferences = sorted({key[0] for key in aggregated})
    series = []

    for row_conference in conferences:
        for keyword in keywords:
            series_name = (
                keyword
                if len(conferences) == 1
                else f"{keyword} ({row_conference})"
            )
            series.append({
                "name": series_name,
                "type": "line",
                "keyword": keyword,
                "conference": row_conference,
                "data": [
                    aggregated.get((row_conference, year, keyword), 0)
                    for year in years
                ],
            })

    data = [
        {
            "year": year,
            "conference": row_conference,
            "keyword": keyword,
            "count": aggregated[(row_conference, year, keyword)],
        }
        for row_conference in conferences
        for keyword in keywords
        for year in years
        if (row_conference, year, keyword) in aggregated
    ]

    return {
        "years": years,
        "conferences": conferences,
        "keywords": keywords,
        "series": series,
        "data": data,
    }
