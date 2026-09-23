"""Canonical paper storage used by search, analysis, detail and CRUD APIs."""

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PAPER_FILE = PROJECT_ROOT / "data" / "papers.json"
LEGACY_LIST_FILE = PROJECT_ROOT / "data_cvpr2024.json"
LEGACY_DETAIL_FILE = PROJECT_ROOT / "cvpr2024_detail.json"

ALLOWED_FIELDS = {
    "title",
    "authors",
    "abstract",
    "keywords",
    "year",
    "conference",
    "pdf",
    "url",
}


class PaperValidationError(ValueError):
    """Raised when a paper payload does not satisfy the API contract."""


class DuplicatePaperError(ValueError):
    """Raised when a paper title already exists."""


def _read_json(path):
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise PaperValidationError(f"資料檔案格式錯誤：{path.name} 必須是陣列")

    return data


def _as_string(value, field, *, allow_empty=True):
    if value is None:
        value = ""

    if not isinstance(value, str):
        raise PaperValidationError(f"{field} 必須是字串")

    value = value.strip()
    if not allow_empty and not value:
        raise PaperValidationError(f"{field} 不可為空")

    return value


def _as_string_list(value, field):
    if value is None:
        return []

    if isinstance(value, str):
        value = [item.strip() for item in value.split(",")]

    if not isinstance(value, list) or any(
        not isinstance(item, str) for item in value
    ):
        raise PaperValidationError(f"{field} 必須是字串陣列")

    return [item.strip() for item in value if item.strip()]


def _as_year(value, *, required):
    if value in (None, ""):
        if required:
            raise PaperValidationError("year 不可為空")
        return None

    try:
        year = int(value)
    except (TypeError, ValueError) as error:
        raise PaperValidationError("year 必須是整數") from error

    if not 1900 <= year <= 2100:
        raise PaperValidationError("year 必須介於 1900 到 2100")

    return year


def normalize_paper(data, *, partial=False):
    """Validate and normalize an API paper payload."""
    if not isinstance(data, dict):
        raise PaperValidationError("請提供 JSON 物件")

    unknown_fields = set(data) - ALLOWED_FIELDS
    if unknown_fields:
        fields = ", ".join(sorted(unknown_fields))
        raise PaperValidationError(f"不支援的欄位：{fields}")

    if not partial:
        for field in ("title", "year", "conference"):
            if field not in data:
                raise PaperValidationError(f"缺少必要欄位：{field}")

    normalized = {}

    if "title" in data:
        normalized["title"] = _as_string(
            data["title"],
            "title",
            allow_empty=False,
        )

    if "authors" in data:
        normalized["authors"] = _as_string_list(data["authors"], "authors")

    if "abstract" in data:
        normalized["abstract"] = _as_string(data["abstract"], "abstract")

    if "keywords" in data:
        normalized["keywords"] = _as_string_list(data["keywords"], "keywords")

    if "year" in data:
        normalized["year"] = _as_year(data["year"], required=not partial)

    if "conference" in data:
        normalized["conference"] = _as_string(
            data["conference"],
            "conference",
            allow_empty=False,
        )

    for field in ("pdf", "url"):
        if field in data:
            normalized[field] = _as_string(data[field], field)

    if not partial:
        normalized.setdefault("authors", [])
        normalized.setdefault("abstract", "")
        normalized.setdefault("keywords", [])
        normalized.setdefault("pdf", "")
        normalized.setdefault("url", "")

    if partial and not normalized:
        raise PaperValidationError("至少要提供一個可修改欄位")

    return normalized


def _canonical_record(paper):
    """Fill defaults for legacy records while preserving one stable schema."""
    normalized = normalize_paper(
        {
            "title": paper.get("title", ""),
            "authors": paper.get("authors", []),
            "abstract": paper.get("abstract", ""),
            "keywords": paper.get("keywords", []),
            "year": paper.get("year", 2024),
            "conference": paper.get("conference", "CVPR"),
            "pdf": paper.get("pdf", ""),
            "url": paper.get("url", ""),
        }
    )
    return normalized


def _load_legacy_papers():
    basic_papers = _read_json(LEGACY_LIST_FILE)
    detail_by_title = {
        paper.get("title"): paper
        for paper in _read_json(LEGACY_DETAIL_FILE)
        if paper.get("title")
    }

    merged = []
    seen_titles = set()

    for basic_paper in basic_papers:
        title = basic_paper.get("title", "")
        detail = detail_by_title.get(title, {})
        merged.append(_canonical_record({**basic_paper, **detail}))
        seen_titles.add(title)

    for detail in detail_by_title.values():
        if detail.get("title") not in seen_titles:
            merged.append(_canonical_record(detail))

    return merged


def load_papers():
    if PAPER_FILE.exists():
        return [_canonical_record(paper) for paper in _read_json(PAPER_FILE)]

    return _load_legacy_papers()


def save_papers(papers):
    normalized = [_canonical_record(paper) for paper in papers]
    PAPER_FILE.parent.mkdir(parents=True, exist_ok=True)
    temporary_file = PAPER_FILE.with_suffix(PAPER_FILE.suffix + ".tmp")
    temporary_file.write_text(
        json.dumps(normalized, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temporary_file.replace(PAPER_FILE)

