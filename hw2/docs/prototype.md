# Prototype Design

## 設計工具

Figma


## Prototype Link

https://www.figma.com/make/teCO9vF14tqYqQH7IZGKiF/CVPR-2024-%E8%AB%96%E6%96%87%E5%88%86%E6%9E%90%E7%B3%BB%E7%B5%B1%E5%8E%9F%E5%9E%8B?t=tDX7lF7LE8RM9mR3-20&fullscreen=1


## Prototype 目的

本原型用於展示 CVPR 2024 論文搜尋與頂會熱詞分析系統之操作流程。

透過 Prototype 模擬使用者從論文搜尋、熱門研究方向分析、關鍵詞關聯探索以及熱度趨勢查看的完整操作流程。


## Prototype 頁面

### 1. Dashboard 首頁

展示：

- 系統總覽
- 論文搜尋入口
- Top 10 熱門研究方向
- 分析圖表


### 2. 論文搜尋頁

展示：

- 關鍵詞搜尋
- 搜尋結果列表
- 論文詳細資料入口


### 3. 論文詳細資料頁

展示：

- Title
- Authors
- Year
- Conference
- PDF
- URL
- Related Keywords


### 4. 熱門研究方向分析頁

展示：

- Top 10 熱門關鍵詞
- 論文數量統計
- 熱門方向排行


### 5. 關鍵詞關聯圖譜頁

展示：

- Keyword Network
- 關鍵詞節點
- 關聯關係


### 6. 熱度趨勢分析頁

展示：

- 不同年份研究詞熱度變化
- Diffusion 與 Transformer 趨勢比較


## Prototype 與實作對應

| Prototype 功能 | 系統實作 |
|---|---|
| 論文搜尋 | Flask Search API |
| 詳細資料展示 | Paper Detail API |
| 熱門方向分析 | analysis.py |
| 關鍵詞圖譜 | keyword-network API |
| 熱度趨勢 | trend API |


## AI 協作紀錄

本 Prototype 使用 AI 協助進行：

- 系統需求整理
- 頁面規劃
- UI 元件配置建議

最後依照實際系統功能調整 Prototype 內容。