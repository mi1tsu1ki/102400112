# 程式碼風格規範

> Python 部分來源：[PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/)  
> Vue 部分來源：[Vue.js Style Guide](https://vuejs.org/style-guide/)

## Python

- 使用 4 個空白縮排，不使用 Tab。
- 每行最多 79 個字元；長表達式使用括號換行。
- 類別使用 `PascalCase`，函式、變數與模組使用 `snake_case`。
- 匯入依標準函式庫、第三方套件、專案模組分組，並保持未使用匯入為零。
- 公開函式與複雜邏輯提供簡短 docstring。
- 使用明確例外處理；不可用空的 `except` 靜默忽略錯誤。

## Vue 3 與 JavaScript

- 元件名稱使用多字詞命名，避免與 HTML 原生元素衝突。
- 優先使用 Vue 3 Composition API 與 `<script setup>`（若使用單檔元件）。
- Props 需明確宣告型別與必要性，事件名稱使用 kebab-case。
- JavaScript 變數與函式使用 `camelCase`，常數使用描述性名稱。
- 模板屬性使用一致的雙引號，避免在模板中放置複雜運算邏輯。
- 列表渲染提供穩定且唯一的 `key`；非必要不使用 `v-if` 與 `v-for` 在同一元素。
- 元件樣式優先局部化，並維持清楚的元件結構與單一職責。
