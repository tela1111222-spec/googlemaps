from flask import Blueprint, request, jsonify

# 定義 hazard 模組的 Blueprint，負責即時路況與路障回報
hazard_bp = Blueprint('hazard', __name__)

@hazard_bp.route('/api/hazard/report', methods=['POST'])
def report_hazard():
    """
    用路人主動一鍵回報突發路障 API。
    
    HTTP 方法: POST
    對應模板: 無 (純 API 路由，回傳 JSON)
    輸入參數 (JSON Body):
        - lat (float, 必填): 障礙點緯度
        - lng (float, 必填): 障礙點經度
        - hazard_type (str, 必填): 路障類型 ('accident' / 'construction' / 'obstacle')
        - description (str, 選填): 補充說明細節
        
    處理邏輯:
        1. 接收並驗證 JSON 欄位（`lat`, `lng`, `hazard_type`），若格式有誤則回傳 400 Bad Request。
        2. 呼叫 `HazardReport.create(lat, lng, hazard_type, description)` 寫入 SQLite。
        3. 前端接收到成功回應後，執行樂觀更新，立即在地圖上渲染出警示圖標。
        
    輸出結果 (200 OK):
        ```json
        {
          "status": "success",
          "hazard_id": 12,
          "message": "Hazard reported successfully"
        }
        ```
    """
    pass

@hazard_bp.route('/api/hazard/list', methods=['GET'])
def list_hazards():
    """
    讀取使用者周邊指定半徑內的所有即時路障。
    
    HTTP 方法: GET
    對應模板: 無 (純 API 路由，回傳 JSON)
    輸入參數 (Query Parameters):
        - lat (float, 必填): 搜尋中心點緯度
        - lng (float, 必填): 搜尋中心點經度
        - radius_degree (float, 選填): 搜尋經緯度範圍半徑，預設 0.05 (約 5km)
        
    處理邏輯:
        1. 讀取並驗證中心點與半徑參數。
        2. 呼叫 `HazardReport.get_nearby(lat, lng, radius_degree)` 從資料庫拉取所有活躍中的障礙點。
        3. 回傳 GeoJSON 格式或點陣列以利前端在地圖上進行圖標標示。
    """
    pass

@hazard_bp.route('/api/hazard/<int:hazard_id>/upvote', methods=['POST'])
def upvote_hazard(hazard_id):
    """
    用路人按讚覆核路障 API（用以核實與防刷機制）。
    
    HTTP 方法: POST
    對應模板: 無 (純 API 路由，回傳 JSON)
    輸入參數 (URL):
        - hazard_id (int, 必填): 路障的唯一識別 ID
        
    處理邏輯:
        1. 呼叫 `HazardReport.upvote(hazard_id)` 將資料庫中該筆資料的 `votes` 數值加 1。
        2. 若該 ID 不存在，回傳 404 Not Found。
        3. 成功後回傳更新後的完整路障欄位 JSON。
    """
    pass
