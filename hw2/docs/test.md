# 可重現測試紀錄

## 測試環境

- Python：3.14.5
- Flask、Flask-CORS
- 測試框架：Python 標準函式庫 `unittest`
- 前端語法檢查：Node.js `node --check`

## 執行方式

在專案根目錄執行：

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
node --check frontend/script.js
```

若要手動啟動服務：

```powershell
.\.venv\Scripts\python.exe backend\api.py
```

## 自動化測試內容

`tests/test_api.py` 包含以下案例：

| 案例 | 驗證內容 |
|---|---|
| 搜尋 | `/search?q=diffusion` 成功回應，結果最多 20 筆 |
| 趨勢 | `top=3` 只產生有限 series，年份為 2022、2023、2024 |
| 趨勢錯誤 | `top=31` 回傳 400 與錯誤訊息 |
| CRUD 驗證 | 空 JSON 回傳 400 |
| CRUD 新增 | 有效資料回傳 201 |
| 重複資料 | 相同標題回傳 409 |
| CRUD 一致性 | 新增後可由 search 找到，修改後欄位更新 |
| CRUD 刪除 | 成功刪除回傳 200，再次刪除回傳 404 |

## 最近一次結果

```text
Ran 5 tests
OK
```

測試使用系統暫存目錄保存 CRUD 測試資料，不會修改正式的 `data/papers.json`。

另外以啟動中的 Flask 服務進行一次 HTTP smoke test：首頁、搜尋、論文詳情、Top 10、關鍵詞圖譜與 Trend 均成功回應；CRUD 實際回傳 POST 201、PUT 200、DELETE 200，臨時資料已刪除。

前端語法檢查 `node --check frontend/script.js` 通過。

## 手動 API 展示流程

```text
GET  /                         服務檢查
GET  /search?q=diffusion       論文搜尋
GET  /paper/<title>            詳細資料
GET  /topics                   Top 10
GET  /keyword-network          關鍵詞圖譜
GET  /trend?top=10             趨勢圖資料
POST /paper                    新增論文
PUT  /paper/<title>            修改論文
DELETE /paper/<title>          刪除論文
```

手動測試 CRUD 時，請使用測試資料標題，測試完成後刪除，避免污染 `data/papers.json`。
