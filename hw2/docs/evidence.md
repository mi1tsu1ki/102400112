# AI 協作與測試證據紀錄

## 一、AI 協作方式

本專案開發過程中使用 AI 輔助進行需求分析、程式設計討論、錯誤排查與文件整理。

AI 主要協助內容包含：

* 分析作業需求與功能拆解
* 協助設計系統架構
* 討論 Flask API 設計方式
* 協助前後端資料格式規劃
* 協助分析錯誤訊息與除錯方向
* 協助整理 README、NABCD、PSP 文件

所有程式碼修改皆由開發者確認後整合，並透過實際執行測試驗證。

---

# 二、AI 協作流程

開發流程如下：

1. 分析作業需求

   * 確認系統需要包含：

     * 論文搜尋
     * 詳細資料展示
     * 熱門方向分析
     * 關鍵詞關聯圖
     * 熱度趨勢分析
     * CRUD 功能
     * 文件與版本管理

2. 系統設計討論

   使用 Flask 作為後端 API Framework：

   ```
   backend/
   ├── api.py
   ├── search.py
   ├── detail.py
   ├── analysis.py
   ├── trend.py
   └── crud.py
   ```

   前端使用：

   ```
   frontend/
   ├── index.html
   ├── style.css
   └── script.js
   ```

3. 功能開發與驗證

   每完成一項功能後：

   * 啟動 Flask Server
   * 使用瀏覽器測試
   * 使用 Thunder Client 測試 API
   * 確認回傳資料格式

---

# 三、AI 協助完成項目

## 1. 論文搜尋系統

完成：

* CVPR 2024 論文資料整理
* 關鍵字搜尋 API
* 前端搜尋介面

驗證：

```
GET /search?q=keyword
```

可正常取得搜尋結果。

---

## 2. 論文詳細資料展示

完成：

* Title
* Authors
* Year
* Conference
* PDF
* URL

驗證：

```
GET /paper/<title>
```

可正常回傳 JSON 資料。

---

## 3. 資料分析功能

完成：

* Top 10 熱門研究方向
* 關鍵詞關聯圖
* 熱度趨勢分析

驗證：

```
GET /topics

GET /keyword-network

GET /trend
```

皆可正常回傳資料。

---

## 4. CRUD 功能

完成：

新增：

```
POST /paper
```

修改：

```
PUT /paper/<title>
```

刪除：

```
DELETE /paper/<title>
```

測試工具：

* Thunder Client

測試結果：

* 新增成功
* 修改成功
* 刪除成功

---

# 四、人工驗證紀錄

AI 提供建議後，由開發者進行：

* 程式執行測試
* API 測試
* 前端操作測試
* Git 版本確認

測試環境：

```
Python 3.14.5

Flask

Flask-CORS

ECharts
```

啟動方式：

```powershell
.\.venv\Scripts\python.exe backend\api.py
```

服務位置：

```
http://127.0.0.1:5000
```

---

# 五、Git 版本紀錄

主要版本：

```
v1.0.0
```

目前包含：

* 系統初版
* 搜尋功能
* 詳細資料展示
* 分析圖表
* CRUD
* 文件整理
* PSP
* NABCD
* 原型設計

主要 commit：

```
bd8ab07 補充PSP實際工時與偏差分析

f434827 新增論文CRUD功能

390cd5b 更新README完整專案說明

fef44c2 新增Figma原型設計文件

afc2515 新增PSP與NABCD需求分析文件
```

---

# 六、目前限制

目前尚未完成：

* 華為雲部署
* 多頂會資料整合
* 大規模年份趨勢分析

後續可依作業需求持續擴充。

---

# 七、總結

本專案透過 AI 輔助完成需求分析、系統設計、程式開發與文件整理。

AI 作為開發輔助工具提供：

* 設計建議
* 問題分析
* 文件整理

最終功能與程式品質仍由開發者自行測試與確認。