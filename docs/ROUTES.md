# API 路由與頁面設計文件 (ROUTES.md)

本文件規劃「機車安全速限警示與預告系統」的 Flask 路由（Routes），包含每個頁面的 URL 路徑、HTTP 方法、輸入/輸出、處理邏輯與對應的 Jinja2 模板。

---

## 1. 路由總覽表格

| 功能 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
|---|---|---|---|---|
| 導航主頁 (地圖與儀表板) | GET | `/` | `app/templates/map.html` | 顯示 Leaflet 地圖、車速儀表板與超速變紅警示遮罩，啟動 GPS 監測。 |
| 偏好設定頁面 | GET | `/settings` | `app/templates/settings.html` | 顯示警告聲開關、超速警示閾值及接近比例設定表單。 |
| 更新偏好設定 | POST | `/settings` | — | 接收並更新使用者警示設定，更新後重導向回設定頁面。 |
| 查詢當前路段速限 | POST | `/api/speed-limit` | — | 接收 GPS 座標，查詢並回傳當前路段的法定速限與道路名稱（JSON 格式）。 |
| 前方速限預告查詢 | POST | `/api/route/preview` | — | 接收當前 GPS 座標，查詢前方 300 公尺是否有速限降低變化（JSON 格式）。 |

---

## 2. 每個路由的詳細說明

### 2.1 導航主頁 (地圖與儀表板)
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

---

### 2.2 偏好設定頁面
* **URL 路徑**：`/settings`
* **HTTP 方法**：`GET`
* **對應模板**：`app/templates/settings.html` (繼承 `base.html`)
* **輸入**：無
* **處理邏輯**：
  * 呼叫 `UserSettings.get_settings()` 獲取當前使用者的警示設定。
  * 將設定傳遞至 `settings.html` 渲染。
* **輸出**：
  * 渲染後的 HTML 設定頁面。
* **錯誤處理**：
  * 若資料庫異常，使用 Default UserSettings 執行渲染，並用 Flash 提示使用者。

---

### 2.3 更新偏好設定
* **URL 路徑**：`/settings`
* **HTTP 方法**：`POST`
* **對應模板**：無 (重導向)
* **輸入**：
  * **表單欄位 (form-data)**:
    * `warning_threshold`: 超速警告門檻（整數，單位 km/h，必填）
    * `enable_voice_alert`: 是否播放警告聲（整數 0 或 1，必填）
    * `approaching_alert_ratio`: 接近速限警告比率（浮點數，如 0.9，必填）
* **處理邏輯**：
  * 驗證表單欄位資料。
  * 呼叫 `UserSettings.update_settings(warning_threshold, enable_voice_alert, approaching_alert_ratio)` 更新 SQLite 資料庫。
  * 成功後發送 Flash 成功訊息，並重導向回 `/settings`。
* **輸出**：
  * 302 重導向至 `/settings`。
* **錯誤處理**：
  * 若欄位格式不符或遺失，重導向回 `/settings` 並顯示 Flash 錯誤提示。

---

### 2.4 查詢當前路段速限
* **URL 路徑**：`/api/speed-limit`
* **HTTP 方法**：`POST`
* **對應模板**：無 (純 API 回傳 JSON)
* **輸入**：
  * **JSON Body**:
    ```json
    {
      "latitude": 25.0421,
      "longitude": 121.5400
    }
    ```
* **處理邏輯**：
  * 接收 JSON 請求，驗證 `latitude` 與 `longitude` 是否存在。
  * 呼叫 `RoadSpeedLimit.find_nearest(latitude, longitude)` 查詢最近的道路段與距離。
  * 若距離在合理範圍內（例如 50 公尺內），則視為騎士行駛在該路段，獲取其法定速限；若太遠則回傳預設速限。
* **輸出**：
  * **JSON Response (200 OK)**:
    ```json
    {
      "status": "success",
      "road_name": "忠孝東路三段",
      "speed_limit": 50,
      "distance": 11.12
    }
    ```
* **錯誤處理**：
  * 若缺少經緯度，回傳 400 Bad Request：
    ```json
    {
      "status": "error",
      "message": "Missing latitude or longitude parameter"
    }
    ```

---

### 2.5 前方速限預告查詢
* **URL 路徑**：`/api/route/preview`
* **HTTP 方法**：`POST`
* **對應模板**：無 (純 API 回傳 JSON)
* **輸入**：
  * **JSON Body**:
    ```json
    {
      "latitude": 25.0420,
      "longitude": 121.5410
    }
    ```
* **處理邏輯**：
  * 接收當前 GPS 座標。
  * 呼叫 `RoadSpeedLimit.find_nearest(latitude, longitude)` 找到當前行駛路段。
  * 檢查該路段是否有前方速限變化（`upcoming_limit` 與 `upcoming_lat`/`upcoming_lng`）。
  * 若有，計算當前位置到預告點的距離。如果距離在 300 公尺內且速限低於當前速限，則回傳預告警示資訊。
* **輸出**：
  * **JSON Response (200 OK)**:
    ```json
    {
      "status": "success",
      "trigger_preview": true,
      "upcoming_limit": 40,
      "distance_to_change": 201.48
    }
    ```
* **錯誤處理**：
  * 若無速限變化或距離大於 300 公尺，回傳 `trigger_preview: false`。

---

## 3. Jinja2 模板清單

### 3.1 `app/templates/base.html`
* **功能**：系統共用網頁版型。
* **區塊定義**：
  * `{% block content %}`：子頁面主體渲染區。
  * `{% block extra_js %}`：子頁面特定 JavaScript 載入區（地圖初始化、GPS 定位等）。
* **全域元件**：包含頂部導覽列（「地圖儀表板」與「偏好設定」連結）、Leaflet.js 地圖庫的 CDN CSS/JS。

### 3.2 `app/templates/map.html`
* **繼承**：`base.html`
* **功能**：導航與警示主畫面。
* **主要 UI 元件**：
  * 地圖展示區塊 (ID: `map`)。
  * 疊加的「即時車速/速限」圓形儀表板。
  * 超速時覆蓋全螢幕的紅色閃爍遮罩（CSS 動畫）。
  * 前方 300m 速限降低的預告圖示面板。
  * 「開始導航」解鎖語音功能的大按鈕。

### 3.3 `app/templates/settings.html`
* **繼承**：`base.html`
* **功能**：警示偏好設定畫面。
* **主要 UI 元件**：
  * 警告閾值設定（+0, +5, +10 km/h）下拉選單。
  * 聲音警示開關（啟用/禁用）。
  * 接近警告比例（85%、90%、95% 觸發黃色警示）滑桿。
  * 送出儲存按鈕與 Flash 提示區。
