import argparse
import json
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup


PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_FILE = PROJECT_ROOT / "data_cvpr2024.json"
OUTPUT_FILE = PROJECT_ROOT / "cvpr2024_detail.json"

DEFAULT_LIMIT = 50
DEFAULT_RETRIES = 3
DEFAULT_DELAY = 0.5
DEFAULT_RETRY_DELAY = 2.0
DEFAULT_TIMEOUT = 15


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Batch crawl CVPR paper detail pages with resume support."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help="Maximum number of papers from the input list to process.",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=DEFAULT_RETRIES,
        help="Maximum request attempts for one paper.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_DELAY,
        help="Delay between papers in seconds.",
    )
    parser.add_argument(
        "--retry-delay",
        type=float,
        default=DEFAULT_RETRY_DELAY,
        help="Initial delay before retrying a failed request.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help="Request timeout in seconds.",
    )
    return parser.parse_args()


def load_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_results(results):
    temporary_file = OUTPUT_FILE.with_suffix(OUTPUT_FILE.suffix + ".tmp")

    try:
        temporary_file.write_text(
            json.dumps(results, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary_file.replace(OUTPUT_FILE)
    finally:
        if temporary_file.exists():
            temporary_file.unlink()


def parse_detail_page(html, source_paper):
    soup = BeautifulSoup(html, "html.parser")

    detail = {
        "title": "",
        "authors": [],
        "year": "",
        "conference": "",
        "pdf": "",
        "url": source_paper["url"],
    }

    for meta in soup.find_all("meta"):
        name = (meta.get("name") or "").lower()
        content = meta.get("content")

        if not name or not content:
            continue

        if name == "citation_title":
            detail["title"] = content
        elif name == "citation_author":
            detail["authors"].append(content)
        elif name == "citation_publication_date":
            detail["year"] = content
        elif name == "citation_conference_title":
            detail["conference"] = content
        elif name == "citation_pdf_url":
            detail["pdf"] = content

    if not detail["title"]:
        detail["title"] = source_paper["title"]

    return detail


def fetch_detail(session, paper, retries, retry_delay, timeout):
    for attempt in range(1, retries + 1):
        try:
            response = session.get(paper["url"], timeout=timeout)
            response.raise_for_status()
            return parse_detail_page(response.text, paper)
        except requests.RequestException as error:
            status_code = error.response.status_code if error.response else None
            is_non_retryable_client_error = (
                status_code is not None
                and 400 <= status_code < 500
                and status_code != 429
            )

            print(
                f"    請求失敗，第 {attempt}/{retries} 次："
                f"{error}"
            )

            if attempt == retries or is_non_retryable_client_error:
                raise

            time.sleep(retry_delay * attempt)


def main():
    args = parse_arguments()

    if args.limit <= 0:
        raise ValueError("--limit 必須大於 0")
    if args.retries <= 0:
        raise ValueError("--retries 必須大於 0")
    if args.delay < 0 or args.retry_delay < 0 or args.timeout <= 0:
        raise ValueError("delay、retry-delay 不可小於 0，timeout 必須大於 0")

    papers = load_json(INPUT_FILE)
    existing_results = load_json(OUTPUT_FILE) if OUTPUT_FILE.exists() else []
    existing_titles = {
        paper.get("title")
        for paper in existing_results
        if paper.get("title")
    }

    selected_papers = papers[:args.limit]
    results = list(existing_results)
    failures = []

    print(f"輸入論文總數：{len(papers)}")
    print(f"本次處理上限：{len(selected_papers)}")
    print(f"既有詳細資料：{len(existing_titles)}")

    session = requests.Session()
    session.headers.update({
        "User-Agent": "CVPR2024PaperSearch/1.0 (educational project)",
    })

    for index, paper in enumerate(selected_papers, start=1):
        title = paper.get("title", "")

        if title in existing_titles:
            print(f"[{index}/{len(selected_papers)}] 跳過（已存在）：{title}")
            continue

        print(f"[{index}/{len(selected_papers)}] 取得：{title}")

        try:
            detail = fetch_detail(
                session=session,
                paper=paper,
                retries=args.retries,
                retry_delay=args.retry_delay,
                timeout=args.timeout,
            )
            results.append(detail)
            existing_titles.add(title)
            save_results(results)

            missing_fields = [
                field
                for field in ("authors", "year", "conference", "pdf")
                if not detail[field]
            ]
            if missing_fields:
                print(
                    "    成功保存，但欄位缺失："
                    + ", ".join(missing_fields)
                )
            else:
                print("    成功保存")

        except (requests.RequestException, ValueError, KeyError) as error:
            failures.append({
                "title": title,
                "url": paper.get("url", ""),
                "error": str(error),
            })
            print(f"    最終失敗：{error}")

        time.sleep(args.delay)

    print()
    print("批次處理完成")
    print(f"目前詳細資料總數：{len(results)}")
    print(f"失敗數量：{len(failures)}")

    if failures:
        print("失敗項目：")
        for failure in failures:
            print(f"- {failure['title']} | {failure['error']}")
        print("失敗項目未寫入結果檔，下次重新執行時會再次嘗試。")


if __name__ == "__main__":
    main()
