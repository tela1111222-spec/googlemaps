from flask import Blueprint, request, jsonify

# 定義 alert 模組的 Blueprint，負責測速與待轉警示
alert_bp = Blueprint('alert', __name__)

@alert_bp.route('/api/alert/check', methods=['GET'])
def check_alerts():
    """
    GPS 即時警示比對 API。
    
    HTTP 方法: GET
    對應模板: 無 (純 API 路由，回傳 JSON)
    輸入參數 (Query Parameters):
        - lat (float, 必填): 使用者當前 GPS 緯度
        - lng (float, 必填): 使用者當前 GPS 經度
        
    處理邏輯:
        1. 接收並驗證 `lat` 與 `lng` 參數，若格式不符或缺失則回傳 400 Bad Request。
        2. 呼叫 `SpeedCamera.get_nearby(lat, lng)` 空間查詢 500m 範圍內的測速相機。
        3. 呼叫 `TwoStageTurn.get_nearby(lat, lng)` 空間查詢 300m 範圍內的兩段式待轉路口。
        4. 限制處理延遲在 500 毫秒以內，即時回傳包含測速限速、相機距離、待轉警示等欄位的 JSON。
        
    輸出結果 (200 OK):
        ```json
        {
          "status": "success",
          "cameras": [
            { "id": 1, "latitude": 25.033, "longitude": 121.564, "speed_limit": 50, "description": "基隆路光復南路口北向" }
          ],
          "hook_turns": [
            { "id": 5, "latitude": 25.035, "longitude": 121.566, "description": "信義路光復南路口" }
          ]
        }
        ```
    """
    pass
