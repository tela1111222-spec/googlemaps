from flask import Blueprint, request, jsonify
import sys
from app.models.camera import SpeedCamera
from app.models.two_stage_turn import TwoStageTurn

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
        1. 接收並驗證 `lat` 與 `lng` 參數。若缺失或格式有誤，則回傳 400 Bad Request。
        2. 呼叫 `SpeedCamera.get_nearby(lat, lng)` 空間查詢 500m 範圍內的測速相機。
        3. 呼叫 `TwoStageTurn.get_nearby(lat, lng)` 空間查詢 300m 範圍內的兩段式待轉路口。
        4. 回傳包含測速限速、相機距離、待轉警示等欄位的 JSON。
        
    輸出結果 (200 OK):
        回傳附近測速點與待轉路口的清單。
    """
    lat_str = request.args.get('lat')
    lng_str = request.args.get('lng')
    
    if not lat_str or not lng_str:
        return jsonify({"status": "error", "message": "缺少必要的 GPS 經緯度參數 (lat, lng)"}), 400
        
    try:
        lat = float(lat_str)
        lng = float(lng_str)
    except ValueError:
        return jsonify({"status": "error", "message": "經緯度參數格式不正確，必須為浮點數"}), 400
        
    try:
        # 進行附近 500m (0.005度) 的測速點檢索
        nearby_cameras = SpeedCamera.get_nearby(lat, lng, radius_degree=0.005)
        
        # 進行附近 300m (0.003度) 的待轉路口檢索
        nearby_turns = TwoStageTurn.get_nearby(lat, lng, radius_degree=0.003)
        
        # 轉換為 dict 列表
        cameras_list = []
        for cam in nearby_cameras:
            cameras_list.append({
                "id": cam.id,
                "latitude": cam.latitude,
                "longitude": cam.longitude,
                "speed_limit": cam.speed_limit,
                "description": cam.description
            })
            
        turns_list = []
        for turn in nearby_turns:
            turns_list.append({
                "id": turn.id,
                "latitude": turn.latitude,
                "longitude": turn.longitude,
                "description": turn.description
            })
            
        return jsonify({
            "status": "success",
            "cameras": cameras_list,
            "hook_turns": turns_list
        })
    except Exception as e:
        print(f"檢索警示資料庫時發生未預期錯誤: {e}", file=sys.stderr)
        return jsonify({"status": "error", "message": "伺服器內部查詢錯誤"}), 500
