from backend.storage import (
    DuplicatePaperError,
    load_papers,
    normalize_paper,
    save_papers,
)


def add_paper(paper):
    normalized = normalize_paper(paper)
    papers = load_papers()

    if any(item["title"] == normalized["title"] for item in papers):
        raise DuplicatePaperError("同標題論文已存在")

    papers.append(normalized)
    save_papers(papers)
    return normalized


def update_paper(title, new_data):
    papers = load_papers()
    normalized = normalize_paper(new_data, partial=True)

    for paper in papers:
        if paper["title"] != title:
            continue

        new_title = normalized.get("title", title)
        if new_title != title and any(
            item["title"] == new_title for item in papers
        ):
            raise DuplicatePaperError("新的論文標題已存在")

        paper.update(normalized)
        save_papers(papers)
        return paper

    return None


def delete_paper(title):
    papers = load_papers()
    remaining = [paper for paper in papers if paper["title"] != title]

    if len(remaining) == len(papers):
        return False

    save_papers(remaining)
    return True
