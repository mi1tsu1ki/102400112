import json


with open("data_cvpr2024.json", "r", encoding="utf-8") as f:
    papers = json.load(f)


print("總論文數:", len(papers))

print("\n前5筆資料:")
for i, p in enumerate(papers[:5]):
    print("----------------")
    print("標題:", p["title"])
    print("網址:", p["url"])