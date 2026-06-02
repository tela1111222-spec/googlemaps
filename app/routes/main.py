from flask import Blueprint, render_template, request, jsonify

# 定義 main 模組的 Blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    首頁 (主地圖頁面) 的路由。
    
    HTTP 方法: GET
    對應模板: app/templates/map.html
    輸入參數: 無
    處理邏輯: 
        直接渲染並回傳地圖首頁 (map.html)，提供使用者輸入目的地、選擇避開條件以及切換高對比模式的介面。
    """
    return render_template('map.html')

@main_bp.route('/api/routes/calculate', methods=['POST'])
def calculate_route():
    """
    計算個人化路線的 API 路由。
    
    HTTP 方法: POST
    對應模板: 無 (API 路由，回傳 JSON)
    輸入參數 (JSON):
        - destination (str, 選填): 目的地的名稱或地址
        - start_coords (list, 選填): 起點經緯度 [lat, lng]
        - end_coords (list, 選填): 終點經緯度 [lat, lng]
        - avoid_highways (bool, 選填): 是否避開高架/快速道路
        - prefer_wide_roads (bool, 選填): 是否偏好寬敞大路
    處理邏輯:
        1. 接收並驗證 JSON 請求。若無有效 JSON 則回傳 400 Bad Request。
        2. 根據 avoid_highways 與 prefer_wide_roads 等偏好，模擬動態加權路線規劃。
        3. 產出平滑且符合特定偏好的經緯度座標序列，封裝為標準 GeoJSON LineString 格式。
        4. 限制整體計算時間低於 3 秒。
    輸出結果:
        - 成功 (200 OK): 回傳 GeoJSON 路線、預估行車時間、距離與狀態。
        - 失敗 (400): 回傳錯誤訊息。
    """
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "無效的 JSON 請求"}), 400
        
    destination = data.get('destination')
    start_coords = data.get('start_coords')
    end_coords = data.get('end_coords')
    
    if not destination and not end_coords:
        return jsonify({"status": "error", "message": "缺失目的地或終點座標"}), 400
        
    avoid_highways = data.get('avoid_highways', False)
    prefer_wide_roads = data.get('prefer_wide_roads', False)
    
    # 預設起點 (例如台北市政府週邊)
    start_lat = start_coords[0] if start_coords else 25.03748
    start_lng = start_coords[1] if start_coords else 121.56477
    
    # 預設終點 (例如信義路區段)
    end_lat = end_coords[0] if end_coords else 25.03367
    end_lng = end_coords[1] if end_coords else 121.56443
    
    # 動態產生中繼導航點，模擬個人化加權繞道效果
    coordinates = []
    steps = 15
    for i in range(steps + 1):
        t = i / steps
        # 線性插值
        lat = start_lat + (end_lat - start_lat) * t
        lng = start_lng + (end_lng - start_lng) * t
        
        # 偏好條件加權：避開高架 -> 往北偏繞行平面大路
        if avoid_highways and 0.2 < t < 0.8:
            lat += 0.0008
            lng += 0.0004
            
        # 偏好條件加權：偏好大路 -> 往南偏繞行主幹道
        if prefer_wide_roads and 0.3 < t < 0.9:
            lat -= 0.0004
            lng -= 0.0002
            
        # GeoJSON 規範座標為 [經度, 緯度] (即 [lng, lat])
        coordinates.append([lng, lat])
        
    # 計算預估時間與距離 (模擬參數)
    duration = 10 if avoid_highways else 6
    distance = 1500 if avoid_highways else 950
    
    route_geojson = {
        "type": "Feature",
        "geometry": {
            "type": "LineString",
            "coordinates": coordinates
        },
        "properties": {
            "destination": destination or "自訂導航終點",
            "avoid_highways": avoid_highways,
            "prefer_wide_roads": prefer_wide_roads,
            "duration_minutes": duration,
            "distance_meters": distance
        }
    }
    
    return jsonify({
        "status": "success",
        "route_geojson": route_geojson
    })
