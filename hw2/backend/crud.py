import json
import os


DATA_FILE = "cvpr2024_detail.json"


def load_papers():

    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)



def save_papers(papers):

    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(
            papers,
            file,
            ensure_ascii=False,
            indent=4
        )



def add_paper(paper):

    papers = load_papers()

    papers.append(paper)

    save_papers(papers)

    return paper



def update_paper(title, new_data):

    papers = load_papers()

    for paper in papers:

        if paper["title"] == title:

            paper.update(new_data)

            save_papers(papers)

            return paper


    return None



def delete_paper(title):

    papers = load_papers()

    new_papers = [
        paper
        for paper in papers
        if paper["title"] != title
    ]


    if len(new_papers) == len(papers):
        return False


    save_papers(new_papers)

    return True