# Google Maps 地圖導航系統 - 系統流程圖與資料流設計

本文件詳細規劃了 **Google Maps 地圖導航系統** 的使用者操作路徑 (User Flow)、系統內部互動序列 (Sequence Diagram) 以及詳細的後端路由功能對照表，為開發團隊提供清晰的實作邏輯指南。

---

## 1. 使用者流程圖 (User Flow)

這張流程圖描述了用路人從進入系統、設定個人化條件、進行導航、即時警示與路況回報，一直到抵達目的地並查看歷史紀錄的完整操作路徑。

```mermaid
flowchart TD
    Start([使用者開啟地圖系統]) --> InitRoute[首頁：載入地圖並定位當前位置]
    
    %% 操作分流
    InitRoute --> Options{選擇操作項目}
    
    %% 分流1：個人化設定與導航
    Options -->|"1. 規劃導航"| InputDest[輸入目的地]
    InputDest --> SetPref[勾選個人化路徑偏好<br/>1. 避開高架/隧道<br/>2. 偏好路幅較寬大路]
    SetPref --> CalcRoute[系統計算並顯示個人化路線]
    
    CalcRoute --> SatisfiedCheck{是否滿意路線？}
    SatisfiedCheck -->|"否，重新設定"| SetPref
    SatisfiedCheck -->|"是，開始導航"| StartNav[啟動導航狀態與語音播報]
    
    %% 導航環節 (即時循環)
    StartNav --> Loop[行進中：系統每 1-2 秒比對 GPS]
    Loop --> AlertCheck{偵測前方警告點？}
    
    AlertCheck -->|"偵測到測速相機"| CameraAlert[1. 畫面超速閃紅警示<br/>2. 免費 TTS 播報限速]
    AlertCheck -->|"偵測到待轉路口"| HookAlert[1. 顯示兩段式左轉圖示<br/>2. TTS 語音提醒待轉]
    AlertCheck -->|"偵測到即時路障"| ObstacleAlert[1. 地圖標註路障位置<br/>2. 觸發動態重新規劃路徑]
    AlertCheck -->|"無警示點"| NormalNav[地圖上順暢前行]
    
    CameraAlert --> NavControl
    HookAlert --> NavControl
    ObstacleAlert --> NavControl
    NormalNav --> NavControl
    
    %% 導航中互動與結束
    NavControl{導航中操作}
    NavControl -->|"主動回報路障"| ReportHazard[點選按鈕，一鍵回報事故/施工]
    ReportHazard --> OptimisticUpdate[前端地圖立即更新標記<br/>並發送至伺服器]
    OptimisticUpdate --> Loop
    
    NavControl -->|"抵達目的地"| EndNav[結束導航]
    EndNav --> SaveHistory[系統自動將行程資料加密儲存]
    SaveHistory --> Options
    
    %% 分流2：偏好與模式切換
    Options -->|"2. 介面設定"| ToggleTheme[開啟/關閉高對比或夜間模式]
    ToggleTheme --> InitRoute
    
    %% 分流3：歷史行程
    Options -->|"3. 歷史紀錄"| ViewHistory[進入歷史行程頁面]
    ViewHistory --> DecryptShow[系統解密並呈現過去的路線軌跡]
    DecryptShow --> Options
```

---

## 2. 系統序列圖 (Sequence Diagram)

為清晰呈現「前端地圖 UI」、「後端 Flask Controller」、「Database Model」與「SQLite」的職責，以下拆解為兩個核心場景的序列圖。

### 場景 A：發起導航與個人化路線規劃
本圖說明使用者在設定偏好後，系統如何快速計算並回傳 GeoJSON 路線格式。

```mermaid
sequenceDiagram
    autonumber
    actor User as 用路人
    participant UI as 瀏覽器地圖 (map.js)
    participant NavJS as 導航模組 (navigation.js)
    participant Flask as Flask (route_pref.py)
    participant Model as Route Model
    participant DB as SQLite
    
    User->>UI: 1. 輸入終點、勾選「避開高架」與「偏好大路」
    UI->>NavJS: 2. 觸發路線規劃請求
    NavJS->>Flask: 3. POST /api/route/calculate (起訖座標, 偏好參數)
    Flask->>Model: 4. 呼叫路徑規劃演算法 (避開高架=True, 大路權重提高)
    Model->>DB: 5. 查詢受偏好影響之道路權重與障礙物座標
    DB-->>Model: 6. 回傳路網拓樸與障礙點
    Model-->>Model: 7. 進行 Dijktra / A* 權重路徑計算
    Model-->>Flask: 8. 回傳最優個人化路線節點 (Coordinates List)
    Flask-->>NavJS: 9. 回傳路線 GeoJSON 格式 (確保在 3 秒內)
    NavJS->>UI: 10. 於地圖上動態描繪紫色個人化路線
    UI-->>User: 11. 語音提示：「路徑規劃完成，已為您避開高架橋，開始導航」
```

### 場景 B：行進中即時 GPS 定位警示與路障回報
本圖說明行車中即時檢索 500m 內警告點，以及用路人一鍵回報路障的資料流。

```mermaid
sequenceDiagram
    autonumber
    actor User as 用路人
    participant AlertJS as 定位警示 (alert.js)
    participant HazardJS as 路障回報 (hazard.js)
    participant Flask as Flask (alert.py / hazard.py)
    participant Model as Database Model
    participant DB as SQLite

    Note over User, AlertJS: 【即時定位警示輪詢 (每 1~2 秒)】
    AlertJS->>Flask: 1. GET /api/alert/check?lat={y}&lng={x} (傳送當前 GPS)
    Flask->>Model: 2. 空間矩形查詢半徑 500m 內測速照相與待轉路口
    Model->>DB: 3. SQL SELECT BETWEEN (優化索引查詢)
    DB-->>Model: 4. 回傳範圍內之警告點資訊
    Model-->>Flask: 5. 回傳警告點 JSON (測速限速、待轉標示)
    Flask-->>AlertJS: 6. 回傳警示 API 回應 (延遲 < 500ms)
    alt 接近測速照相
        AlertJS->>User: 7.1. 畫面閃紅警報、呼叫瀏覽器 TTS 語音播報速限
    else 接近待轉路口
        AlertJS->>User: 7.2. 顯示兩段式左轉圖示、語音提示前方待轉
    end

    Note over User, HazardJS: 【主動路障回報場景】
    User->>HazardJS: 8. 發現車禍，點擊「一鍵回報車禍」
    HazardJS->>User: 9. 樂觀更新：地圖上立即繪製車禍標記
    HazardJS->>Flask: 10. POST /api/hazard/report (回報坐標, 類型="車禍")
    Flask->>Model: 11. 寫入路障回報模型 (含檢驗防洗防刷機制)
    Model->>DB: 12. INSERT INTO hazards (儲存回報)
    DB-->>Model: 13. 確認寫入成功
    Model-->>Flask: 14. 儲存成功
    Flask-->>HazardJS: 15. 回傳儲存成功 API 回應
```

---

## 3. 功能清單與 API 對照表

本系統的所有頁面與背景 API 設計如下，完全支援 MVC 模式並確保功能解耦：

| 功能模組 | 功能名稱 | URL 路徑 | HTTP 方法 | 傳入參數 (Request) | 傳出內容 (Response) | 說明 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **View (首頁)** | 首頁導航地圖 | `/` | `GET` | 無 | HTML 網頁 | 渲染包含 Leaflet 地圖、個人化偏好面板、警示圖示的主要導航介面。 |
| **Controller** | 計算個人化路線 | `/api/route/calculate` | `POST` | `{start: [y,x], end: [y,x], avoid_highways: bool, prefer_wide: bool}` | `GeoJSON` 格式的路線座標與屬性 | 根據起迄點與使用者的偏好設定，動態計算並回傳最佳個人化導航路徑。 |
| **Controller** | GPS 即時警示查詢 | `/api/alert/check` | `GET` | `?lat={y}&lng={x}` | `{cameras: [...], hook_turns: [...]}` | 接收使用者當前定位，回傳半徑 500m 內的待轉路口與測速點資訊。 |
| **Controller** | 回報即時路障 | `/api/hazard/report` | `POST` | `{lat: y, lng: x, type: "accident/construction/obstacle"}` | `{status: "success", hazard_id: int}` | 用路人一鍵回報路上突發狀況，寫入資料庫供其他用路人參考。 |
| **Controller** | 讀取所有路障 | `/api/hazard/list` | `GET` | `?lat={y}&lng={x}&radius_km=5` | `[{id: 1, lat: y, lng: x, type: "accident"}]` | 取得使用者周邊指定半徑內的所有活動路障，用以在地圖上標記。 |
| **View (歷史)** | 歷史行程列表 | `/history` | `GET` | 無 | HTML 網頁 | 讀取 SQLite 中的行程，解密後以清單與軌跡圖渲染給使用者。 |
| **Controller** | 儲存行程紀錄 | `/api/history/save` | `POST` | `{route_name: string, path: [[y,x]], duration: int}` | `{status: "success"}` | 導航結束時，系統自動將行駛路徑、時間等敏感情資「加密」存入資料庫。 |
