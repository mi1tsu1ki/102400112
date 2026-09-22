import sys

from pathlib import Path

from flask import Flask, request, jsonify
from flask_cors import CORS


PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.search import search
from backend.detail import get_paper_detail
from backend.analysis import get_keyword_network, get_top_topics

from backend.trend import get_trend_data

from backend.crud import (
    add_paper,
    update_paper,
    delete_paper
)

app = Flask(__name__)
CORS(app)


@app.route("/")
def home():
    return "CVPR 2024 Paper Search API"


@app.route("/search")
def paper_search():

    keyword = request.args.get("q", "")

    result = search(keyword)

    return jsonify({
        "count": len(result),
        "results": result[:20]
    })


@app.route("/paper/<path:title>")
def paper_detail(title):
    paper = get_paper_detail(title)

    if paper is None:
        return jsonify({"error": "paper not found"}), 404

    return jsonify(paper)


@app.route("/paper", methods=["POST"])
def create_paper():

    data = request.json

    result = add_paper(data)

    return jsonify(result)


@app.route("/paper/<path:title>", methods=["PUT"])
def edit_paper(title):

    data = request.json

    result = update_paper(
        title,
        data
    )

    if result is None:
        return jsonify({
            "error": "paper not found"
        }),404

    return jsonify(result)


@app.route("/paper/<path:title>", methods=["DELETE"])
def remove_paper(title):

    result = delete_paper(title)

    return jsonify({
        "success": result
    })


@app.route("/topics")
def topics():
    return jsonify({
        "topics": get_top_topics(),
    })


@app.route("/keyword-network")
def keyword_network():
    return jsonify(get_keyword_network())


@app.route("/trend")
def trend():

    return {
        "data": get_trend_data()
    }


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )