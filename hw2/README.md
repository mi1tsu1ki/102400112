# CVPR 2024 Paper Search

## 作業資訊

| 項目 | 內容 |
|---|---|
| 課程 | 軟體工程實踐 |
| 作業 | 第二次作業：與 AI 結對編程（頂會熱詞統計） |
| 學號 | 102400112 |

## 專案介紹

本專案提供計算機視覺論文的搜尋、詳細資料展示與研究熱點分析。系統目前以 CVPR 2024 論文為主要資料集，並提供 CVPR/ICCV 初步趨勢資料的視覺化。

目前可使用的功能：

- 論文關鍵字搜尋與原文連結。
- 論文詳細資料查詢。
- Top 10 熱門研究方向。
- 關鍵詞共現圖譜。
- 按年份與會議聚合的熱度趨勢圖。
- 論文新增、修改、刪除 API。

## 資料來源與範圍

`data/papers.json` 是系統目前唯一的論文資料來源，啟動後由 search、detail、analysis 與 CRUD 共用。此檔案由既有資料合併產生，不需要重新爬取詳細頁面：

- 2715 篇 CVPR 2024 論文列表。
- 其中 50 篇來自既有詳細資料；其餘資料保留列表欄位，詳細欄位可能是空白或預設值。
- 尚未重新爬取其餘論文的詳細頁面。

`data_cvpr2024.json` 與 `cvpr2024_detail.json` 保留為原始資料備份；`data/trend_data.json` 是趨勢分析的長表來源，目前包含 CVPR 與 ICCV 的 2022–2024 資料。

## 安裝與啟動

在專案根目錄執行：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
啟動 Flask：

```powershell
.\.venv\Scripts\python.exe backend\api.py
```

服務位址：`http://127.0.0.1:5000`

接著用瀏覽器開啟 `frontend/index.html`。前端圖表使用 ECharts CDN，若離線則圖表無法載入。

## API

| 方法與路徑 | 說明 |
|---|---|
| `GET /` | 檢查服務是否啟動 |
| `GET /search?q=diffusion` | 搜尋論文，最多回傳 20 筆結果 |
| `GET /paper/<title>` | 查詢單篇論文 |
| `POST /paper` | 新增論文，成功回傳 201 |
| `PUT /paper/<title>` | 修改論文 |
| `DELETE /paper/<title>` | 刪除論文，不存在回傳 404 |
| `GET /topics` | 取得 Top 10 熱門詞 |
| `GET /keyword-network` | 取得最多 100 個節點的關聯圖資料 |
| `GET /trend?top=10` | 取得聚合後趨勢資料 |
| `GET /trend?top=10&conference=CVPR` | 篩選單一會議的趨勢資料 |

`/trend` 回傳 `years`、`conferences`、`keywords`、`series` 與聚合後的 `data`。`top` 允許 1–30，避免將原始長表的上萬個 keyword 全部建立成前端 series。

新增與修改論文時，`title`、`year`、`conference` 會進行必要性與型別驗證；重複標題回傳 409，格式錯誤回傳 400，找不到資料回傳 404。

## 測試

使用標準函式庫 unittest，不需要額外安裝 pytest：

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

目前測試涵蓋：

- 搜尋結果上限。
- 趨勢資料年份、Top N 與 series 數量限制。
- 非法趨勢參數的 400 錯誤。
- CRUD 新增、修改、刪除、重複資料、格式驗證與不存在資料的錯誤處理。

## 專案結構

```text
hw2/
├── backend/
│   ├── api.py
│   ├── storage.py
│   ├── search.py
│   ├── detail.py
│   ├── analysis.py
│   ├── trend.py
│   ├── crud.py
│   ├── crawl_cvpr.py
│   ├── crawl_cvpr_detail.py
│   └── crawl_trend_data.py
├── data/
│   ├── papers.json
│   └── trend_data.json
├── tests/
│   └── test_api.py
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
├── docs/
├── data_cvpr2024.json
├── cvpr2024_detail.json
├── requirements.txt
└── README.md
```

## 文件與目前限制

- `docs/NABCD.md`：需求、方法、效益、競品與交付範圍。
- `docs/PSP.md`：估算、實際工時與偏差紀錄。
- `docs/evidence.md`：AI 結對編程案例與驗證證據。
- `docs/test.md`：可重現的測試指令與結果紀錄。
- `docs/prototype.md`：前端原型說明。

目前仍未完成或不在本次收尾範圍的項目：

- 其餘 2665 篇論文的完整詳細資料。
- 完整、可驗證的 ECCV 與更多年份資料。
- 雲端部署與正式服務環境驗證。
- 自動化 CI/CD 與正式 release 流程；目前只整理本機可展示版本。

## Git 工作方式

本次收尾以目前檢出的分支與工作樹為準。提交前請執行測試並檢查：

```powershell
git status
git diff --check
git log --oneline -5
```
