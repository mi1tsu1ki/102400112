import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.detail import load_paper_details


DATA_FILE = PROJECT_ROOT / "data_cvpr2024.json"


def load_paper_details_by_title():
    return {
        paper["title"]: paper
        for paper in load_paper_details()
    }


def searchable_text(paper, detail):
    fields = [
        paper.get("title", ""),
        detail.get("year", ""),
        detail.get("conference", ""),
    ]

    authors = detail.get("authors", [])
    if isinstance(authors, list):
        fields.extend(authors)
    else:
        fields.append(authors)

    return " ".join(str(field) for field in fields if field).lower()


def merge_paper_detail(paper, detail):
    if detail is None:
        return paper

    return {
        **paper,
        **detail,
    }


def load_papers():
    with DATA_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def search(keyword):
    papers = load_papers()
    details = load_paper_details_by_title()
    keyword = keyword.lower()

    result = []

    for paper in papers:
        detail = details.get(paper["title"])

        if keyword in searchable_text(paper, detail or {}):
            result.append(merge_paper_detail(paper, detail))

    return result


if __name__ == "__main__":
    keyword = input("搜尋關鍵字: ")

    result = search(keyword)

    print("找到:", len(result), "篇")

    for i, paper in enumerate(result[:10]):
        print(
            i + 1,
            paper["title"]
        )
