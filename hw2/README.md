# CVPR 2024 Paper Search

## 作業資訊

| 項目 | 內容 |
|---|---|
| 課程 | 軟體工程實踐 |
| 作業 | 第二次作業：與 AI 結對編程（頂會熱詞統計） |
| 作業公告 | https://bbs.csdn.net/topics/620526318 |
| 學號 | 102400112 |

---

# 專案介紹

本專案為軟體工程課程第二次作業，目標是建立一個計算機視覺領域論文搜尋與研究熱點分析系統。

系統以 CVPR 2024 論文資料作為主要資料來源，提供論文搜尋、詳細資料展示、熱門研究方向分析、關鍵詞關聯圖以及熱門詞熱度趨勢分析功能。

透過 Web 介面協助使用者快速搜尋論文，並分析近年計算機視覺領域研究方向變化。

---

# 使用技術

- Python 3.14.5
- Flask
- Flask-CORS
- HTML
- CSS
- JavaScript
- ECharts
- JSON

---

# 資料來源

目前資料來源：

- CVPR 2024 論文公開資料

主要資料檔案：

```
data_cvpr2024.json
```

包含：

```
2715 篇 CVPR 2024 論文列表資料
```

詳細資料：

```
cvpr2024_detail.json
```

目前包含：

```
50 篇論文詳細資料
```

---

# 系統功能

## 1. 論文搜尋

提供：

- 輸入關鍵字搜尋 CVPR 2024 論文標題
- 顯示搜尋結果
- 開啟論文原文連結
- 查看論文詳細資料


## 2. 論文詳細資料展示

提供以下資訊：

- Title
- Authors
- Year
- Conference
- PDF
- URL


## 3. 熱門研究方向分析

根據論文標題進行關鍵詞統計。

功能：

- 分析熱門研究方向
- 展示 Top 10 熱門關鍵詞
- 點擊熱門方向直接搜尋相關論文


## 4. 關鍵詞關聯圖譜

利用論文標題中的關鍵詞建立關聯網路。

展示：

- 節點代表研究關鍵詞
- 邊代表關鍵詞共同出現關係
- 支援點擊節點搜尋相關論文


## 5. 熱門詞熱度趨勢分析

目前展示：

- diffusion
- transformer

分析：

- 2022
- 2023
- 2024

三個年份的熱門詞熱度變化。

使用 ECharts Line Chart 呈現趨勢。

---

# 專案結構

```
hw2/

├── backend/
│   ├── api.py
│   ├── search.py
│   ├── detail.py
│   ├── analysis.py
│   ├── trend.py
│   ├── crawl_cvpr.py
│   └── crawl_cvpr_detail.py
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
│
├── data/
│   └── trend_data.json
│
├── docs/
│   ├── PSP.md
│   ├── NABCD.md
│   └── prototype.md
│
├── data_cvpr2024.json
├── cvpr2024_detail.json
├── requirements.txt
├── README.md
└── codestyle.md
```

---

# 安裝方式

在專案根目錄開啟 PowerShell。

建立虛擬環境：

```powershell
python -m venv .venv
```

啟用虛擬環境：

```powershell
.\.venv\Scripts\Activate.ps1
```

安裝套件：

```powershell
pip install -r requirements.txt
```

---

# 啟動方式

在專案根目錄執行：

```powershell
.\.venv\Scripts\python.exe backend\api.py
```

後端啟動後：

```
http://127.0.0.1:5000
```

接著使用瀏覽器開啟：

```
frontend/index.html
```

即可使用系統。

---

# API 範例

## 搜尋論文

```
GET http://127.0.0.1:5000/search?q=diffusion
```

---

## 熱門研究方向

```
GET http://127.0.0.1:5000/topics
```

---

## 關鍵詞關聯圖

```
GET http://127.0.0.1:5000/keyword-network
```

---

## 熱度趨勢

```
GET http://127.0.0.1:5000/trend
```

---

# Prototype 設計

使用工具：

```
Figma
```

Prototype：

```
https://www.figma.com/make/teCO9vF14tqYqQH7IZGKiF/CVPR-2024-%E8%AB%96%E6%96%87%E5%88%86%E6%9E%90%E7%B3%BB%E7%B5%B1%E5%8E%9F%E5%9E%8B
```

詳細說明：

```
docs/prototype.md
```

---

# AI 使用說明

本專案開發過程使用 AI 作為結對編程助手。

AI 協助內容：

- 需求分析與 NABCD 文件整理
- 系統架構規劃
- Flask API 設計討論
- 前端功能設計討論
- 程式錯誤分析與 Debug
- 文件整理與格式調整

所有 AI 產生內容皆經人工檢查、修改後整合至專案。

---

# 文件

目前包含：

```
docs/

├── PSP.md
├── NABCD.md
└── prototype.md
```

其中：

- PSP.md：專案開發時間規劃與實際紀錄
- NABCD.md：需求分析文件
- prototype.md：Figma 原型設計說明

---

# 目前限制

目前尚未完成：

- 論文新增、修改、刪除 CRUD 功能
- 多頂會資料整合（ICCV、ECCV 等）
- 多年份熱度趨勢動圖
- 華為雲 CodeArts 部署

後續將依照作業需求持續擴充。

---

# Git 開發紀錄

目前採用 Git 進行版本管理。

分支規劃：

- dev：開發分支
- main：穩定版本分支

目前已完成：

- 初始專案建立
- CVPR 資料處理
- 搜尋功能
- 詳細資料展示
- 熱門方向分析
- 關鍵詞圖譜
- 熱度趨勢分析
- 文件整理
- Prototype 設計

目前累積：

```
17 commits
```