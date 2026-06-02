# API 路由與頁面設計文件 (ROUTES.md)

本文件規劃「個人化路徑系統」的 Flask 路由（Routes），包含每個頁面的 URL 路徑、HTTP 方法、輸入/輸出、處理邏輯與對應的 Jinja2 模板。

## 1. 路由總覽表格

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
|---|---|---|---|---|
| 首頁 (主地圖頁面) | GET | `/` | `app/templates/map.html` | 顯示主地圖與搜尋介面，提供偏好條件設定與高對比模式切換入口。 |
| 計算個人化路線 | POST | `/api/routes/calculate` | — | 接收目的地與避開條件，回傳計算後路徑座標（JSON 格式）。 |
| 查看歷史行程列表 | GET | `/history` | `app/templates/history.html` | 讀取所有行程紀錄，並由 Model 自動解密後顯示。 |
| 建立行程紀錄 | POST | `/history` | — | 接收導航完畢的行程資料，將路線資料加密後存入 DB，重導向至列表。 |
| 刪除行程紀錄 | POST | `/history/<int:history_id>/delete` | — | 刪除指定 ID 的歷史行程，刪除後重導向至列表。 |

---

## 2. 每個路由的詳細說明

### 2.1 首頁 (主地圖頁面)
* **URL 路徑**：`/`
* **HTTP 方法**：`GET`
* **對應模板**：`app/templates/map.html` (繼承 `base.html`)
* **輸入**：無
* **處理邏輯**：
  * 直接渲染 `map.html`。
* **輸出**：
  * 渲染後的 HTML 頁面。
* **錯誤處理**：
  * 若模板不存在，Flask 將拋出 500 錯誤。

### 2.2 計算個人化路線
* **URL 路徑**：`/api/routes/calculate`
* **HTTP 方法**：`POST`
* **對應模板**：無 (純 API 回傳 JSON)
* **輸入**：
  * **JSON Body**:
    ```json
    {
      "destination": "台北 101",
      "avoid_conditions": "擁擠路段,危險路口"
    }
    ```
* **處理邏輯**：
  * 接收 JSON 請求，驗證 `destination`。
  * 根據 `avoid_conditions` 計算符合偏好的路線（MVP 階段回傳包含座標序列與模擬路徑的 JSON）。
  * 必須優化演算法以保證在 3 秒內完成計算。
* **輸出**：
  * **JSON Response (200 OK)**:
    ```json
    {
      "status": "success",
      "destination": "台北 101",
      "avoid_conditions": "擁擠路段,危險路口",
      "route_data": "[[121.5645, 25.0338], [121.5650, 25.0340]]"
    }
    ```
* **錯誤處理**：
  * 若缺少 `destination`，回傳 400 Bad Request：
    ```json
    {
      "status": "error",
      "message": "Missing destination parameter"
    }
    ```

### 2.3 查看歷史行程列表
* **URL 路徑**：`/history`
* **HTTP 方法**：`GET`
* **對應模板**：`app/templates/history.html` (繼承 `base.html`)
* **輸入**：無
* **處理邏輯**：
  * 呼叫 `RouteHistory.get_all()` 查詢所有歷史紀錄。
  * `RouteHistory` Model 會自動解密資料庫中 `encrypted_route_data` 欄位的資料，在屬性 `route_data` 提供明文。
* **輸出**：
  * 渲染 `history.html`，並將解密後的歷史紀錄列表傳給模板。
* **錯誤處理**：
  * 若資料庫連線失敗，回傳 500 錯誤頁面。

### 2.4 建立行程紀錄
* **URL 路徑**：`/history`
* **HTTP 方法**：`POST`
* **對應模板**：無 (重導向)
* **輸入**：
  * **表單欄位 (form-data)**:
    * `destination`: 目的地名稱或地址 (必填)
    * `avoid_conditions`: 避開的條件（如「擁擠路段」, 選填）
    * `route_data`: 路線座標點明文字串 (必填)
* **處理邏輯**：
  * 驗證必填欄位。
  * 呼叫 `RouteHistory.create(destination, avoid_conditions, route_data)`，該方法將對 `route_data` 進行加密後存入 SQLite 資料庫。
  * 儲存成功後，使用 `redirect(url_for('history.list_history'))` 重導向。
* **輸出**：
  * 302 重導向至 `/history`。
* **錯誤處理**：
  * 若缺少必要參數，重導向回首頁，並利用 Flask flash 顯示錯誤。

### 2.5 刪除行程紀錄
* **URL 路徑**：`/history/<int:history_id>/delete`
* **HTTP 方法**：`POST`
* **對應模板**：無 (重導向)
* **輸入**：
  * **URL 參數**: `history_id` (整數，必填)
* **處理邏輯**：
  * 呼叫 `RouteHistory.delete(history_id)` 從 SQLite 資料庫移除該筆資料。
  * 執行完成後，重導向回行程記錄列表。
* **輸出**：
  * 302 重導向至 `/history`。
* **錯誤處理**：
  * 若該 ID 不存在，直接重導向回 `/history` 並利用 Flask flash 提示錯誤。

---

## 3. Jinja2 模板清單

### 3.1 `app/templates/base.html`
* **功能**：系統共用版型（全域布局）。
* **區塊定義**：
  * `{% block content %}`：供子模板置入主體畫面。
  * `{% block extra_js %}`：供子模板置入額外的前端 Javascript（如 Google Maps API 初始化等）。
* **元件**：包含全域導覽列（包含「首頁地圖」與「歷史行程」連結）、全域 CSS 引入。

### 3.2 `app/templates/map.html`
* **繼承**：`base.html`
* **功能**：核心地圖操作與導航頁面。
* **元件**：
  * 目的地搜尋框、避開條件複選框 (避開擁擠路段、避開危險路口)。
  * 高對比導航模式切換開關 (開啟時為網頁套用 `.high-contrast` 類別)。
  * 地圖展示區塊 (ID: `map`)。
  * 語音提醒功能載入。

### 3.3 `app/templates/history.html`
* **繼承**：`base.html`
* **功能**：歷史行程清單頁面。
* **元件**：
  * 歷史紀錄表格（顯示欄位：目的地、避開條件、建立時間、解密後的路徑）。
  * 刪除按鈕（每個項目都有一個小型 POST 表單，以呼叫 `/history/<id>/delete` 路由）。
