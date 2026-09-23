def load_paper_details():
    from backend.storage import load_papers

    return load_papers()


def get_paper_detail(title):
    for paper in load_paper_details():
        if paper["title"] == title:
            return paper

    return None
