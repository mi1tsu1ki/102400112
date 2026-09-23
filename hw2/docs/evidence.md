# 收尾與驗證證據

本文件只記錄目前工作樹中可以由檔案、命令輸出或 Git 狀態確認的內容；未實際執行的瀏覽器操作、部署與外部服務不寫成已完成。

## 一、目前資料範圍

- `data/papers.json`：2715 篇 canonical 論文資料。
- `cvpr2024_detail.json`：50 篇既有詳細資料。
- `data/trend_data.json`：17,922 筆趨勢長表，包含 CVPR 與 ICCV 的資料；不包含可宣稱完整的 ECCV 多年資料。
- 本次沒有重新爬取其餘 2665 篇詳細資料。

## 二、本次程式收尾

1. 統一 search、detail、analysis 與 CRUD 使用 `data/papers.json`。
2. `/trend` 依 conference、year、keyword 聚合，並限制 `top` 為 1–30，前端只繪製有限數量的 series。
3. CRUD 加入必要欄位、型別、年份、重複標題與不存在資料的錯誤處理。
4. 保留現有 Flask 頁面與 ECharts 前端，不進行大規模重構。

## 三、自動化驗證

執行指令：

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m compileall -q backend tests
node --check frontend/script.js
```

本輪目前已確認：

- `tests/test_api.py`：5 個 unittest 通過。
- Python `compileall`：通過。
- `node --check frontend/script.js`：通過。
- Flask HTTP smoke test：首頁、搜尋、詳情、Top 10、關鍵詞圖譜、Trend 成功；CRUD 的 POST 201、PUT 200、DELETE 200 成功。
- CRUD 測試資料寫入系統暫存目錄，未污染正式資料檔。

測試涵蓋搜尋上限、Trend Top N 與錯誤參數、首頁、Top 10、關鍵詞圖譜，以及 CRUD 新增、修改、刪除、重複資料、格式錯誤與不存在資料。

## 四、尚未宣稱完成的項目

- 2715 篇完整詳細資料。
- ECCV 或完整多年、跨會議趨勢資料。
- 華為雲或其他正式環境部署。
- 新的正式 Release 或 CI/CD 流程。

既有 `main` 分支與 `v1.0.0` tag 可由 Git 歷史查到，但不把它們當成本輪收尾修改的 Release 證據。
