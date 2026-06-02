# Google Maps 地圖導航系統 - API 路由與頁面設計文件 (ROUTES.md)

本文件規劃 **Google Maps 地圖導航系統** 的 Flask 路由（Routes），包括每個頁面的 URL 路徑、HTTP 方法、輸入與輸出、處理邏輯，以及對應的 Jinja2 HTML 模板。設計完全契合 Flask 的 MVC 模式，並已將邏輯解耦至對應的模組骨架中。

---

## 1. 路由總覽表格

本系統的頁面路由與背景 API 定義如下：

| 功能模組 | 功能名稱 | HTTP 方法 | URL 路徑 | 對應模板 | 說明 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **View (首頁)** | 首頁導航地圖頁面 | `GET` | `/` | `app/templates/map.html` | 顯示主地圖、搜尋欄、個人化設定面板，支援日夜/高對比視覺模式切換。 |
| **Controller** | 計算個人化路線 API | `POST` | `/api/route/calculate` | — | 接收起迄點座標與自訂偏好，回傳計算好的 GeoJSON 路線資料。 |
| **Controller** | GPS 即時定位警示 API | `GET` | `/api/alert/check` | — | 接收當前 GPS，快速查詢 500m 內的待轉路口與測速點資訊。 |
| **Controller** | 一鍵回報即時路障 API | `POST` | `/api/hazard/report` | — | 用路人主動提交路上的車禍、施工或路障。 |
| **Controller** | 查詢周邊所有路障 API | `GET` | `/api/hazard/list` | — | 拉取周邊範圍內的所有活動路障，用以在地圖上標記。 |
| **Controller** | 覆核/按讚即時路障 API | `POST` | `/api/hazard/<int:hazard_id>/upvote` | — | 其他用路人一鍵覆核路障真實性，累加 votes 數值。 |
| **View (歷史)** | 歷史行程紀錄頁面 | `GET` | `/history` | `app/templates/history.html` | 讀取所有行程紀錄，由 Model 自動解密後以清單與軌跡圖顯示。 |
| **Controller** | 儲存行程紀錄 API | `POST` | `/api/history/save` | — | 導航抵達終點後，自動加密儲存本次行駛路徑、時間與偏好。 |
| **Controller** | 刪除歷史行程 API | `POST` | `/api/history/<int:history_id>/delete` | — | 刪除指定的歷史行程記錄，完成後重導向至列表。 |

---

## 2. 每個路由的詳細說明

### 2.1. 導航與地圖 (View & Route Calculation)

#### 2.1.1. 首頁導航地圖頁面
* **URL 路徑**：`/`
* **HTTP 方法**：`GET`
* **對應模板**：`app/templates/map.html` (繼承 `base.html`)
* **輸入 (URL 參數)**：無
* **處理邏輯**：
  - 直接渲染 `map.html`，並加載基礎 OpenStreetMap 圖資與導航操作面板。
* **輸出**：渲染完成的網頁 HTML。

#### 2.1.2. 計算個人化路線 API
* **URL 路徑**：`/api/route/calculate`
* **HTTP 方法**：`POST`
* **對應模板**：無 (純 API 回傳 JSON)
* **輸入 (JSON Body)**：
  ```json
  {
    "start_coords": [25.033, 121.564],
    "end_coords": [25.041, 121.517],
    "avoid_highways": true,
    "prefer_wide_roads": true
  }
  ```
* **處理邏輯**：
  1. 讀取並驗證起迄座標 `start_coords` 與 `end_coords`（必填），若不符則回傳 400 Bad Request。
  2. 根據避開高架 (`avoid_highways`) 與偏好大路 (`prefer_wide_roads`) 參數，計算權重路徑。
  3. 確保演算法在 **3 秒內** 回傳，回傳路線的 GeoJSON 格式。
* **輸出 (200 OK JSON)**：
  ```json
  {
    "status": "success",
    "route_geojson": { "type": "Feature", "geometry": { "type": "LineString", "coordinates": [...] } },
    "avoid_conditions": "avoid_highways,prefer_wide_roads"
  }
  ```

---

### 2.2. GPS 即時警示 (GPS Alert Polling)

#### 2.2.1. GPS 即時定位警示 API
* **URL 路徑**：`/api/alert/check`
* **HTTP 方法**：`GET`
* **對應模板**：無 (純 API 回傳 JSON)
* **輸入 (Query Parameters)**：
  - `lat`: 使用者當前 GPS 緯度 (float, 必填)
  - `lng`: 使用者當前 GPS 經度 (float, 必填)
* **處理邏輯**：
  1. 接收經緯度坐標。
  2. 呼叫 `SpeedCamera.get_nearby(lat, lng)` 快速查詢 500m 內測速照相與路段限速。
  3. 呼叫 `TwoStageTurn.get_nearby(lat, lng)` 查詢 300m 內待轉路口。
  4. 回應延遲控制在 **500 毫秒**以內。
* **輸出 (200 OK JSON)**：
  ```json
  {
    "status": "success",
    "cameras": [{ "id": 1, "latitude": 25.033, "longitude": 121.564, "speed_limit": 50, "description": "基隆路光復南路口北向" }],
    "hook_turns": [{ "id": 5, "latitude": 25.035, "longitude": 121.566, "description": "信義路光復南路口" }]
  }
  ```

---

### 2.3. 即時路況與障礙回報 (Hazard Reporting)

#### 2.3.1. 一鍵回報即時路障 API
* **URL 路徑**：`/api/hazard/report`
* **HTTP 方法**：`POST`
* **對應模板**：無 (純 API 回傳 JSON)
* **輸入 (JSON Body)**：
  ```json
  {
    "lat": 25.038,
    "lng": 121.559,
    "hazard_type": "accident",
    "description": "外側車道兩機車擦撞，輕微回堵"
  }
  ```
* **處理邏輯**：
  1. 驗證坐標與 `'accident'/'construction'/'obstacle'` 等合法類型，不符回傳 400。
  2. 呼叫 `HazardReport.create` 寫入 SQLite。
  3. 前端進行樂觀更新 (Optimistic Update) 立即標記地圖。
* **輸出 (200 OK JSON)**：
  ```json
  {
    "status": "success",
    "hazard_id": 12,
    "message": "Hazard reported successfully"
  }
  ```

#### 2.3.2. 查詢周邊所有路障 API
* **URL 路徑**：`/api/hazard/list`
* **HTTP 方法**：`GET`
* **輸入 (Query Parameters)**：
  - `lat`, `lng` (必填)
  - `radius_degree` (選填，預設 0.05 ≈ 5km)
* **處理邏輯**：
  - 呼叫 `HazardReport.get_nearby` 拉取周邊範圍內所有的活躍路障。
* **輸出**：路障資料 JSON 列表。

#### 2.3.3. 覆核即時路障 API
* **URL 路徑**：`/api/hazard/<int:hazard_id>/upvote`
* **HTTP 方法**：`POST`
* **處理邏輯**：
  - 將對應路障之 `votes` (覆核票數) 累加 1。
* **輸出**：回傳最新該路障之 JSON 結構。若 ID 不存在回傳 404。

---

### 2.4. 行程歷史紀錄 (History Management)

#### 2.4.1. 歷史行程紀錄頁面
* **URL 路徑**：`/history`
* **HTTP 方法**：`GET`
* **對應模板**：`app/templates/history.html`
* **處理邏輯**：
  - 呼叫 `RouteHistory.get_all()` 拉取所有歷史。Model 會在讀取屬性 `route_data` 時**自動解密** Base64 加密字串，返回明文給模板渲染。
* **輸出**：歷史列表與軌跡圖的 HTML 網頁。

#### 2.4.2. 儲存行程紀錄 API
* **URL 路徑**：`/api/history/save`
* **HTTP 方法**：`POST`
* **輸入 (JSON Body)**：
  ```json
  {
    "destination": "台北 101",
    "avoid_conditions": "避開高架",
    "route_data": "[[121.5645, 25.0338], [121.5650, 25.0340]]"
  }
  ```
* **處理邏輯**：
  - 驗證參數，呼叫 `RouteHistory.create(destination, avoid_conditions, route_data)`，在寫入 SQLite 前自動將 `route_data` 加密防範外洩。
* **輸出**：成功 JSON。

#### 2.4.3. 刪除歷史行程 API
* **URL 路徑**：`/api/history/<int:history_id>/delete`
* **HTTP 方法**：`POST`
* **處理邏輯**：
  - 呼叫 `RouteHistory.delete(history_id)` 從 SQLite 刪除該行程，完成後 `redirect(url_for('history.list_history'))`。
* **輸出**：302 重導向回 `/history`。

---

## 3. Jinja2 HTML 模板清單

所有的視圖頁面模板規劃如下：

### 3.1. `app/templates/base.html`
* **功能**：全域佈局共用底版。
* **區塊 (Blocks)**：
  - `{% block content %}`：子模板的主畫面承載區。
  - `{% block extra_js %}`：子模板引入專屬 JS（如地圖載入與控制）。
* **元件**：全域導航列（地圖導航、歷史紀錄）、全域 CSS 樣式、日夜間/高對比切換公共按鈕。

### 3.2. `app/templates/map.html`
* **繼承**：`base.html`
* **功能**：核心導航地圖頁面。
* **主要 UI 元件**：
  - 搜尋目的地輸入框與「開始規劃」按鈕。
  - 個人化路線偏好設定選單（避開高架/偏好大路）。
  - 地圖展示視窗 (ID: `map`，利用 Leaflet 渲染)。
  - 即時警告提示框（待轉圖示警告、超速閃紅提示）。
  - 即時路障回報按鈕一覽（一鍵提交事故/施工/路障）。

### 3.3. `app/templates/history.html`
* **繼承**：`base.html`
* **功能**：解密行程的歷史列表。
* **主要 UI 元件**：
  - 行程列表卡片（顯示目的地、偏好條件、日期、時間）。
  - 「在圖上查看」軌跡瀏覽器。
  - 「刪除此行程」按鈕（獨立 POST Form 提交至 `/api/history/<id>/delete`）。
