import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DETAIL_FILE = PROJECT_ROOT / "cvpr2024_detail.json"


def load_paper_details():
    with DETAIL_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_paper_detail(title):
    for paper in load_paper_details():
        if paper["title"] == title:
            return paper

    return None
