# 整合個人化路徑系統流程圖

## 1. 使用者流程圖 (User Flow)

這張流程圖描述了使用者從進入系統到完成路線導航與查看歷史紀錄的完整操作路徑。

```mermaid
flowchart LR
    A(["使用者開啟網站"]) --> B["首頁 - 地圖與搜尋介面"]
    
    B --> C{"選擇操作"}
    
    C -->|"切換視覺"| D["開啟/關閉高對比模式"]
    D --> B
    
    C -->|"查看紀錄"| E["進入歷史行程頁面"]
    E --> F["瀏覽過去加密儲存的路線"]
    F --> B
    
    C -->|"規劃路線"| G["輸入目的地"]
    G --> H["設定個人化條件<br>(例如：避開特定擁擠/危險路段)"]
    H --> I["系統計算並顯示推薦路徑"]
    I --> J{"是否滿意路線？"}
    J -->|"否"| H
    J -->|"是"| K["開始導航"]
    K --> L["啟用語音導航播報"]
    L --> M(["抵達目的地並結束導航"])
```

## 2. 系統序列圖 (Sequence Diagram)

此序列圖展示了當使用者規劃路線並在導航結束後儲存紀錄時，資料在系統內部（前端、Flask 路由、資料庫）的流動方式。

```mermaid
sequenceDiagram
    actor User as 使用者
    participant Browser as 瀏覽器 (前端 JS)
    participant Flask as Flask (Controller)
    participant Model as Database Model
    participant DB as SQLite

    User->>Browser: 1. 輸入目的地與避開條件，點擊「規劃路線」
    Browser->>Flask: 2. POST /api/routes/calculate
    Flask->>Model: 3. 處理路徑計算與條件過濾
    Model-->>Flask: 4. 回傳最佳路線資料
    Flask-->>Browser: 5. 回傳路線結果 (需於 3 秒內)
    
    User->>Browser: 6. 確認路線並點擊「開始導航」
    Browser->>Browser: 7. 啟動地圖導航與語音播報
    
    User->>Browser: 8. 抵達目的地，結束導航
    Browser->>Flask: 9. POST /history (儲存行程)
    Flask->>Model: 10. 將行程資料進行加密
    Model->>DB: 11. INSERT INTO history (儲存加密資料)
    DB-->>Model: 12. 儲存成功
    Model-->>Flask: 13. 確認儲存
    Flask-->>Browser: 14. 回傳儲存成功訊息
```

## 3. 功能清單對照表

以下為系統核心功能與其對應的 URL 路徑、HTTP 方法及說明。

| 功能名稱 | URL 路徑 | HTTP 方法 | 說明 |
|---|---|---|---|
| 首頁 (地圖與導航) | `/` | GET | 渲染主地圖頁面，提供搜尋與條件設定介面（含高對比切換按鈕） |
| 計算個人化路線 | `/api/routes/calculate` | POST | 接收目的地與偏好條件，回傳計算後的路徑座標資料（JSON 格式） |
| 儲存行程紀錄 | `/history` | POST | 接收完成導航的行程資料，將其加密後儲存至資料庫 |
| 查看歷史行程 | `/history` | GET | 渲染歷史紀錄列表頁面，從資料庫讀取並解密顯示給使用者 |
