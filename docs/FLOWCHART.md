# 機車路口待轉預告系統流程圖

## 1. 使用者流程圖 (User Flow)

這張流程圖描述了機車騎士從進入系統、設定警示偏好，到開啟導航（模擬或真實 GPS）、即時比對待轉路口、倒數剩餘公尺，以及環境感光夜間降亮的完整操作與體驗路徑。

```mermaid
flowchart TD
    A(["使用者開啟網站"]) --> B["首頁 - 地圖與待轉倒數儀表板"]
    
    B --> C{"選擇操作"}
    
    C -->|"警示偏好設定"| D["進入偏好設定頁面"]
    D --> E["調整警示聲開關與亮度降低模式"]
    E --> B
    
    C -->|"開始行駛/導航"| F["點擊「開始導航」 (選擇模擬或真實 GPS)"]
    F --> G["系統啟動定位監控與車速監測"]
    G --> H["即時比對當前經緯度與待轉路口資料庫"]
    
    H --> I{"是否匹配到 50m 內需待轉路口？"}
    I -->|"是"| J["觸發待轉預告：畫面顯示待轉大圖標、語音播放「前方路口請待轉」"]
    J --> K["進入待轉警示區 (50m - 30m)：畫面即時顯示剩餘公尺數倒數，供騎士減速與變道"]
    I -->|"否"| L["維持正常地圖畫面顯示"]
    
    K --> M{"是否抵達路口 (距離 < 30m) 或離開路口？"}
    M -->|"是"| N["隱藏待轉預告與倒數，恢復正常畫面"]
    M -->|"否"| K
    
    L --> O{"是否點擊「停止導航」？"}
    N --> O
    O -->|"是"| P(["結束導航，停止定位監測與重設 UI"])
    O -->|"否"| H
    
    C -->|"環境光線偵測"| Q["感光元件偵測照度 (或判斷系統時間在 18:00 - 06:00)"]
    Q --> R{"環境光線是否小於 10 lux？"}
    R -->|"是"| S["自動套用 .night-mode CSS 暗色護眼濾鏡 (調降螢幕亮度)"]
    R -->|"否"| T["維持或恢復正常明亮顯示模式"]
    S --> B
    T --> B
```

---

## 2. 系統序列圖 (Sequence Diagram)

本系統採混合式即時處理。以下呈現騎士開啟真實 GPS 導航、行經待轉路口時，瀏覽器前端、Flask API 與資料庫模型之間的元件通訊流程。

```mermaid
sequenceDiagram
    actor User as 機車騎士
    participant Browser as 瀏覽器 (前端 JS)
    participant Flask as Flask (Controller)
    participant Model as Intersection Model
    participant DB as SQLite 資料庫

    User->>Browser: 1. 點擊「開始導航」 (觸發解鎖 Speech 語音功能)
    Note over Browser: 啟動 GPS (Geolocation API) 高頻率監聽定位
    
    loop 每秒位置更新
        Browser->>Flask: 2. POST /api/intersection/check (傳送當前 GPS 座標)
        Flask->>Model: 3. 查詢該座標周圍最近的路口與規則
        Model->>DB: 4. SELECT * FROM intersection_limits WHERE ...
        DB-->>Model: 5. 回傳路口資訊 (路口經緯度, 待轉狀態)
        Model-->>Flask: 6. 封裝路口對照模型
        Flask-->>Browser: 7. 回傳 JSON 響應 (need_turn: true, center_lat, center_lng)
        
        Note over Browser: 瀏覽器在本地計算與路口中心的距離 (d)
        
        alt 距離 d 介於 30 至 50 公尺內 (黃金反應區)
            alt 為首次進入該路口警示區
                Browser->>User: 8a. 聽覺警示：播放語音「前方路口請待轉」 (Web Speech API)
            end
            Browser->>User: 8b. 視覺警示：顯示「待轉圖標」與「倒數 d 公尺」
        else 距離 d < 30 公尺 (已抵達/待轉中) 或 d > 50 公尺
            Browser->>User: 9. 隱藏待轉警示，恢復/維持一般導航地圖介面
        end
    end
```

---

## 3. 功能清單對照表

以下為本系統的主要功能、對應的 URL 路徑、HTTP 方法及功能說明。

| 功能名稱 | URL 路徑 | HTTP 方法 | 說明 |
|---|---|---|---|
| **導航首頁 (地圖儀表板)** | `/` | `GET` | 渲染主地圖頁面，包含 Leaflet 地圖、定位狀態、大字體距離倒數與待轉視覺提醒。 |
| **偏好設定頁面** | `/settings` | `GET` | 渲染偏好設定表單，允許騎士設定語音警示開關、警示觸發門檻與亮度調整模式。 |
| **更新偏好設定** | `/settings` | `POST` | 接收表單送出的偏好設定資料並寫入 SQLite 資料庫儲存。 |
| **路口待轉檢查 API** | `/api/intersection/check` | `POST` | 接收騎士目前的經緯度，查詢 50 公尺內是否有符合待轉規則的路口，並回傳路口中心座標。 |
