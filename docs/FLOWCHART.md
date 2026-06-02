# 機車安全速限警示與預告系統流程圖

## 1. 使用者流程圖 (User Flow)

這張流程圖描述了機車騎士從進入系統、設定警示偏好，到開始導航、接收即時超速警示與前方速限預告的完整操作與體驗路徑。

```mermaid
flowchart TD
    A(["使用者開啟網站"]) --> B["首頁 - 地圖與車速顯示器"]
    
    B --> C{"選擇操作"}
    
    C -->|"警示偏好設定"| D["進入偏好設定頁面"]
    D --> E["設定速限警告門檻與是否播放警告音效"]
    E --> B
    
    C -->|"開始行駛/導航"| F["輸入目的地並點擊「開始導航」"]
    F --> G["系統啟動 GPS 定位與車速監測"]
    G --> H["即時比對當前車速與路段速限"]
    
    H --> I{"車速狀態判斷"}
    I -->|"超過速限"| J["觸發超速警示：螢幕背景變紅、播放警告聲"]
    I -->|"接近速限 (如 > 90%)"| K["視覺黃色警示，提醒騎士注意"]
    I -->|"正常車速"| L["顯示正常色彩介面"]
    
    J --> M{"持續監測前方路況"}
    K --> M
    L --> M
    
    M --> N{"前方 300 公尺是否有速限降低變化？"}
    N -->|"是"| O["觸發預告警示：螢幕顯示速限降低圖示"]
    N -->|"否"| P["維持正常狀態"]
    
    O --> Q{"是否抵達目的地？"}
    P --> Q
    
    Q -->|"否"| H
    Q -->|"是"| R(["結束導航並停止定位監測"])
```

## 2. 系統序列圖 (Sequence Diagram)

本系統採混合式即時處理，以下分別展示「即時車速比對警示」與「前方路段速限預告」的元件通訊流程。

### A. 即時車速比對與超速警示流程
```mermaid
sequenceDiagram
    actor User as 機車騎士
    participant Browser as 瀏覽器 (前端 JS)
    participant Flask as Flask (Controller)
    participant Model as Speed Limit Model
    participant DB as SQLite 資料庫

    User->>Browser: 1. 點擊「開始導航」 (觸發解鎖語音功能)
    Note over Browser: 啟動 GPS (Geolocation API) 監聽
    Browser->>Flask: 2. POST /api/speed-limit (發送 GPS 座標)
    Flask->>Model: 3. 查詢該座標路段速限
    Model->>DB: 4. SELECT speed_limit FROM road_limits ...
    DB-->>Model: 5. 回傳速限 (如 50)
    Model-->>Flask: 6. 回傳數據
    Flask-->>Browser: 7. 回傳 JSON 響應 (limit: 50)
    
    Note over Browser: 瀏覽器即時比對當前 GPS 車速與速限
    alt 當前車速 > 50 km/h (超速)
        Browser->>User: 8a. 視覺警示：螢幕背景變紅 (CSS style 變更)
        Browser->>User: 8b. 聽覺警示：播放警告聲 (audio.js)
    else 當前車速 介於 45 ~ 50 km/h (接近速限)
        Browser->>User: 9. 視覺提示：顯示黃色警告框
    else 車速 <= 45 km/h (安全範圍)
        Browser->>User: 10. 恢復正常介面顯示
    end
```

### B. 前方路段速限變化預告流程
```mermaid
sequenceDiagram
    participant Browser as 瀏覽器 (前端 JS)
    participant Flask as Flask (Controller)
    participant Model as Speed Limit Model
    participant DB as SQLite 資料庫

    Note over Browser: 車輛沿著導航路徑前進中
    Browser->>Flask: 1. POST /api/route/preview (傳送當前經緯度與規劃路線)
    Flask->>Model: 2. 檢索當前位置前方 300 公尺之路段速限
    Model->>DB: 3. SELECT * FROM road_limits WHERE ...
    DB-->>Model: 4. 回傳前方路段速限資料 (下個路段速限：40)
    Model-->>Flask: 5. 比對發現速限降低 (50 -> 40)
    Flask-->>Browser: 6. 回傳 JSON 預告資料 (upcoming_limit: 40, distance: 300)
    Browser->>Browser: 7. 在畫面上繪製「前方 300m 速限 40」之預告圖示與警語
```

## 3. 功能清單對照表

以下為本系統的主要功能、對應的 URL 路徑、HTTP 方法及詳細功能說明。

| 功能名稱 | URL 路徑 | HTTP 方法 | 說明 |
|---|---|---|---|
| 導航主頁 (地圖與儀表板) | `/` | GET | 渲染系統首頁，包含 Leaflet 地圖、車速計儀表板、變紅警示遮罩等介面。 |
| 偏好設定頁面 | `/settings` | GET | 渲染設定頁面，允許騎士調整速限警示門檻（例如：速限 +5 km/h 才警告）以及音效開關。 |
| 更新偏好設定 | `/settings` | POST | 接收表單提交的偏好設定資料，將設定寫入 SQLite 中進行保存。 |
| 查詢當前路段速限 | `/api/speed-limit` | POST | 接收騎士目前的經緯度，經資料庫比對後回傳該路段的最新速限（JSON 格式）。 |
| 前方速限預告查詢 | `/api/route/preview` | POST | 接收騎士當前位置與前進路線，回傳前方 300 公尺內是否有速限降低之變化資訊。 |
