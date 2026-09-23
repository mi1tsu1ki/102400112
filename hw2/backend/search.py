from backend.storage import load_papers


def load_paper_details_by_title():
    return {
        paper["title"]: paper
        for paper in load_papers()
    }


def searchable_text(paper, detail=None):
    detail = detail or {}
    fields = [
        paper.get("title", ""),
        detail.get("year", ""),
        detail.get("conference", ""),
        detail.get("abstract", ""),
    ]

    authors = detail.get("authors", [])
    if isinstance(authors, list):
        fields.extend(authors)
    else:
        fields.append(authors)

    keywords = detail.get("keywords", [])
    if isinstance(keywords, list):
        fields.extend(keywords)
    else:
        fields.append(keywords)

    return " ".join(str(field) for field in fields if field).lower()


def merge_paper_detail(paper, detail):
    if detail is None:
        return paper

    return {
        **paper,
        **detail,
    }


def search(keyword):
    papers = load_papers()
    keyword = (keyword or "").strip().lower()

    result = []

    for paper in papers:
        if keyword in searchable_text(paper):
            result.append(paper)

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
