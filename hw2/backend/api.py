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
    delete_paper,
)
from backend.storage import DuplicatePaperError, PaperValidationError

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
    data = request.get_json(silent=True)

    try:
        result = add_paper(data)
    except DuplicatePaperError as error:
        return jsonify({"error": str(error)}), 409
    except PaperValidationError as error:
        return jsonify({"error": str(error)}), 400

    return jsonify(result), 201


@app.route("/paper/<path:title>", methods=["PUT"])
def edit_paper(title):
    data = request.get_json(silent=True)

    try:
        result = update_paper(title, data)
    except DuplicatePaperError as error:
        return jsonify({"error": str(error)}), 409
    except PaperValidationError as error:
        return jsonify({"error": str(error)}), 400

    if result is None:
        return jsonify({
            "error": "paper not found"
        }), 404

    return jsonify(result)


@app.route("/paper/<path:title>", methods=["DELETE"])
def remove_paper(title):
    result = delete_paper(title)

    if not result:
        return jsonify({
            "error": "paper not found"
        }), 404

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
    top = request.args.get("top", default="10")
    try:
        top = int(top)
        result = get_trend_data(
            top=top,
            conference=request.args.get("conference"),
        )
    except (TypeError, ValueError) as error:
        return jsonify({"error": str(error)}), 400

    return jsonify(result)


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
