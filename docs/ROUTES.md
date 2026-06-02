# API 路由與頁面設計文件 (ROUTES.md)

本文件規劃「機車路口待轉預告系統」的 Flask 路由（Routes），包含每個頁面的 URL 路徑、HTTP 方法、輸入/輸出、處理邏輯與對應的 Jinja2 模板。

---

## 1. 路由總覽表格

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
|---|---|---|---|---|
| 導航主頁 (地圖與待轉倒數) | GET | `/` | `app/templates/map.html` | 顯示地圖、時速儀表板、待轉大圖標與剩餘公尺倒數，開啟 GPS 定位監控。 |
| 偏好設定頁面 | GET | `/settings` | `app/templates/settings.html` | 顯示語音警示開關、預警公尺距離門檻與自動亮度調整設定表單。 |
| 更新偏好設定 | POST | `/settings` | — | 接收並更新使用者待轉設定參數，成功後重導向回設定頁面。 |
| 查詢最近路口待轉規則 | POST | `/api/intersection/check` | — | 接收 GPS 座標，查詢並回傳 50 公尺內最近的路口待轉規則與路口中心（JSON 格式）。 |

---

## 2. 每個路由的詳細說明

### 2.1 導航主頁 (地圖與儀表板)
* **URL 路徑**：`/`
* **HTTP 方法**：`GET`
* **對應模板**：`app/templates/map.html` (繼承 `base.html`)
* **輸入**：無
* **處理邏輯**：
  - 呼叫 `UserSettings.get_settings()` 獲取使用者偏好參數。
  - 渲染 `map.html` 並傳遞設定變數。
* **輸出**：
  - 渲染後的 HTML 頁面。
* **錯誤處理**：
  - 若模板不存在，Flask 將拋出 500 內部伺服器錯誤。

---

### 2.2 偏好設定頁面
* **URL 路徑**：`/settings`
* **HTTP 方法**：`GET`
* **對應模板**：`app/templates/settings.html` (繼承 `base.html`)
* **輸入**：無
* **處理邏輯**：
  - 呼叫 `UserSettings.get_settings()` 獲取目前使用者的待轉設定參數。
  - 將設定傳遞至 `settings.html` 渲染。
* **輸出**：
  - 渲染後的 HTML 設定頁面。

---

### 2.3 更新偏好設定
* **URL 路徑**：`/settings`
* **HTTP 方法**：`POST`
* **對應模板**：無 (重導向)
* **輸入**：
  - **表單欄位 (form-data)**:
    - `warning_threshold`: 預告觸發門檻距離（整數，公尺）
    - `enable_voice_alert`: 是否播放待轉語音警示（整數 0 或 1）
    - `enable_auto_brightness`: 是否開啟自動亮度調整（整數 0 或 1）
* **處理邏輯**：
  - 驗證表單輸入。
  - 呼叫 `UserSettings.update_settings(...)` 更新資料庫。
  - 傳送 Flash 成功訊息，重導向回 `/settings`。
* **輸出**：
  - 302 重導向至 `/settings`。
* **錯誤處理**：
  - 欄位缺失或格式不合時，重導向回設定頁並以 Flash 顯示錯誤提示。

---

### 2.4 查詢最近路口待轉規則
* **URL 路徑**：`/api/intersection/check`
* **HTTP 方法**：`POST`
* **對應模板**：無 (純 API 回傳 JSON)
* **輸入**：
  - **JSON Body**:
    ```json
    {
      "latitude": 25.0421,
      "longitude": 121.5352
    }
    ```
* **處理邏輯**：
  - 接收 JSON 請求，驗證經緯度欄位是否為浮點數。
  - 呼叫 `IntersectionLimit.find_nearest(latitude, longitude)` 查詢最近的路口。
  - 比對距離：若投影距離大於 50 公尺，回傳 `match: false`；若在 50 公尺內，回傳待轉規則及路口中心座標。
* **輸出**：
  - **JSON Response (200 OK)**:
    ```json
    {
      "status": "success",
      "match": true,
      "intersection_name": "忠孝新生路口 (忠孝新生捷運站旁)",
      "need_two_stage_turn": 1,
      "center_lat": 25.042,
      "center_lng": 121.535,
      "distance": 12.45
    }
    ```
* **錯誤處理**：
  - 若缺少經緯度參數，回傳 400 Bad Request：
    ```json
    {
      "status": "error",
      "message": "缺少必要的經度 (longitude) 或緯度 (latitude) 參數"
    }
    ```

---

## 3. Jinja2 模板規劃

### 3.1 `app/templates/base.html`
* **功能**：全域通用排版。
* **主要區塊**：
  - `{% block content %}`：子頁面核心網頁內容渲染區。
  - `{% block extra_js %}`：子頁面特定的 JavaScript 程式碼置放區。
* **共用元件**：包含頂部導覽列連結、Leaflet.js 相關的 CSS 與 JS CDN 引入、以及 Flash 提示訊息的動態呈現區。

### 3.2 `app/templates/map.html`
* **繼承**：`base.html`
* **功能**：地圖導航與待轉倒數提醒主介面。
* **前端功能邏輯**：
  - 初始化地圖與騎士 Marker。
  - 每秒取得 GPS 經緯度，打 API 至 `/api/intersection/check`。
  - 距離 `50m - 30m` 內，計算騎士與路口中心點之大圓距離並在儀表板中央即時顯示倒數（如：`剩餘 45m`）。
  - 若首次踏入該路段，使用 Web Speech API 語音廣播「前方路口請待轉」。
  - 整合感光感應器（Ambient Light Sensor），若周圍光線微弱，動態為 body 套用 `.night-mode` 調降畫面亮度。

### 3.3 `app/templates/settings.html`
* **繼承**：`base.html`
* **功能**：警示與亮度調整偏好設定介面。
* **主要 UI 元件**：
  - 語音播放開關開關（Switch Toggle）。
  - 預警觸發距離設定（30m, 50m, 70m 單選鈕組）。
  - 自動亮度調整開關。
  - 表單儲存與返回首頁按鈕。
