import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

TREND_FILE = PROJECT_ROOT / "data" / "trend_data.json"



def get_trend_data():

    with TREND_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)