import requests
from bs4 import BeautifulSoup
import json


url = "https://openaccess.thecvf.com/CVPR2024?day=all"

response = requests.get(url, timeout=15)

soup = BeautifulSoup(response.text, "html.parser")


papers = []

for a in soup.find_all("a"):
    href = str(a.get("href"))

    if "/CVPR2024/html/" in href and "_paper.html" in href:
        title = a.get_text(strip=True)

        papers.append({
            "title": title,
            "url": "https://openaccess.thecvf.com" + href
        })


print("論文數量:", len(papers))


with open("data_cvpr2024.json", "w", encoding="utf-8") as f:
    json.dump(
        papers,
        f,
        ensure_ascii=False,
        indent=2
    )


print("完成")