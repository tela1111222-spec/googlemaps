from flask import Blueprint, render_template, request, jsonify
from app.models.speed_limit import RoadSpeedLimit, distance_in_meters

# 定義 main 模組的 Blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    導航主頁 (地圖與儀表板)
    
    HTTP 方法: GET
    對應模板: app/templates/map.html (繼承 base.html)
    說明: 渲染系統首頁，包含 Leaflet 地圖、車速顯示儀表板、超速變紅與前方預告等核心介面。
    """
    from app.models.user_settings import UserSettings
    settings = UserSettings.get_settings()
    return render_template('map.html', settings=settings)

@main_bp.route('/api/speed-limit', methods=['POST'])
def get_speed_limit():
    """
    查詢當前路段速限 API
    
    HTTP 方法: POST
    對應模板: 無 (純 JSON 響應)
    輸入參數 (JSON):
        - latitude (float, 必填): 騎士當前所處緯度
        - longitude (float, 必填): 騎士當前所處經度
    說明: 接收經緯度座標，調用 RoadSpeedLimit 模型查詢最近的路段並回傳其法定最高速限與道路名稱。
    """
    data = request.get_json() or {}
    lat = data.get('latitude')
    lng = data.get('longitude')
    
    if lat is None or lng is None:
        return jsonify({
            "status": "error",
            "message": "缺少必要的緯度 (latitude) 或經度 (longitude) 參數"
        }), 400
        
    try:
        lat = float(lat)
        lng = float(lng)
    except ValueError:
        return jsonify({
            "status": "error",
            "message": "經緯度參數格式錯誤，必須為浮點數"
        }), 400
        
    nearest_road, dist = RoadSpeedLimit.find_nearest(lat, lng)
    
    # 距離大於 50 公尺時視為偏離道路，回傳預設的未知路段與速限 50 km/h
    if not nearest_road or (dist is not None and dist > 50.0):
        return jsonify({
            "status": "success",
            "road_name": "未知路段",
            "speed_limit": 50,
            "distance": dist
        }), 200
        
    return jsonify({
        "status": "success",
        "road_name": nearest_road.road_name,
        "speed_limit": nearest_road.speed_limit,
        "distance": dist
    }), 200

@main_bp.route('/api/route/preview', methods=['POST'])
def preview_route_speed_limit():
    """
    前方路段速限變化預告 API
    
    HTTP 方法: POST
    對應模板: 無 (純 JSON 響應)
    輸入參數 (JSON):
        - latitude (float, 必填): 騎士當前所處緯度
        - longitude (float, 必填): 騎士當前所處經度
    說明: 接收當前經緯度，查詢騎士前進路線上前方 300 公尺處是否有速限降低之變化。
    """
    data = request.get_json() or {}
    lat = data.get('latitude')
    lng = data.get('longitude')
    
    if lat is None or lng is None:
        return jsonify({
            "status": "error",
            "message": "缺少必要的緯度 (latitude) 或經度 (longitude) 參數"
        }), 400
        
    try:
        lat = float(lat)
        lng = float(lng)
    except ValueError:
        return jsonify({
            "status": "error",
            "message": "經緯度參數格式錯誤，必須為浮點數"
        }), 400
        
    nearest_road, dist = RoadSpeedLimit.find_nearest(lat, lng)
    
    # 只有當使用者距離最近的路段在 50 公尺內，才進行前方速限變化檢測
    if nearest_road and dist <= 50.0 and nearest_road.upcoming_limit is not None and nearest_road.upcoming_lat is not None and nearest_road.upcoming_lng is not None:
        # 計算當前位置到前方預告點的實際距離（公尺）
        dist_to_change = distance_in_meters(lat, lng, nearest_road.upcoming_lat, nearest_road.upcoming_lng)
        
        # 距離在 300 公尺以內且速限低於當前速限，則觸發預告
        if dist_to_change <= 300.0:
            return jsonify({
                "status": "success",
                "trigger_preview": True,
                "upcoming_limit": nearest_road.upcoming_limit,
                "distance_to_change": dist_to_change
            }), 200
            
    return jsonify({
        "status": "success",
        "trigger_preview": False
    }), 200
