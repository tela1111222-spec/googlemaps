from flask import Blueprint, request, jsonify
import sys
from app.models.hazard import HazardReport

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
        1. 接收並驗證 JSON 欄位。若格式有誤則回傳 400 Bad Request。
        2. 呼叫 `HazardReport.create(lat, lng, hazard_type, description)` 寫入 SQLite。
        
    輸出結果 (200 OK):
        回傳成功狀態與新建路障的唯一 ID。
    """
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "無效的 JSON 請求"}), 400
        
    lat = data.get('lat')
    lng = data.get('lng')
    hazard_type = data.get('hazard_type')
    description = data.get('description', '')
    
    if lat is None or lng is None or not hazard_type:
        return jsonify({"status": "error", "message": "缺少必要參數 (lat, lng, hazard_type)"}), 400
        
    if hazard_type not in ['accident', 'construction', 'obstacle']:
        return jsonify({"status": "error", "message": "無效的路障類型。只允許: accident, construction, obstacle"}), 400
        
    try:
        lat_val = float(lat)
        lng_val = float(lng)
    except ValueError:
        return jsonify({"status": "error", "message": "經緯度坐標必須為浮點數"}), 400
        
    try:
        new_hazard = HazardReport.create(lat_val, lng_val, hazard_type, description)
        if new_hazard:
            return jsonify({
                "status": "success",
                "hazard_id": new_hazard.id,
                "message": "已成功新增即時路障回報"
            })
        else:
            return jsonify({"status": "error", "message": "建立路障回報失敗"}), 500
    except Exception as e:
        print(f"回報路障時發生伺服器錯誤: {e}", file=sys.stderr)
        return jsonify({"status": "error", "message": "伺服器內部錯誤"}), 500

@hazard_bp.route('/api/hazard/list', methods=['GET'])
def list_hazards():
    """
    讀取使用者周邊指定半徑內的所有即時路障。
    
    HTTP 方法: GET
    對應模板: 無 (純 API 路由，回傳 JSON)
    輸入參數 (Query Parameters):
        - lat (float, 必填): 搜尋中心點緯度
        - lng (float, 必填): 搜尋中心點經度
        - radius_degree (float, 選填): 搜尋範圍半徑，預設 0.05 (約 5km)
    """
    lat_str = request.args.get('lat')
    lng_str = request.args.get('lng')
    radius_str = request.args.get('radius_degree', '0.05')
    
    if not lat_str or not lng_str:
        return jsonify({"status": "error", "message": "缺少必要中心點定位參數 (lat, lng)"}), 400
        
    try:
        lat = float(lat_str)
        lng = float(lng_str)
        radius = float(radius_str)
    except ValueError:
        return jsonify({"status": "error", "message": "參數格式不正確"}), 400
        
    try:
        nearby_hazards = HazardReport.get_nearby(lat, lng, radius_degree=radius)
        hazards_list = []
        for h in nearby_hazards:
            hazards_list.append({
                "id": h.id,
                "latitude": h.latitude,
                "longitude": h.longitude,
                "hazard_type": h.hazard_type,
                "description": h.description,
                "votes": h.votes,
                "created_at": h.created_at
            })
        return jsonify({
            "status": "success",
            "hazards": hazards_list
        })
    except Exception as e:
        print(f"取得周邊路障失敗: {e}", file=sys.stderr)
        return jsonify({"status": "error", "message": "無法取得周邊路障"}), 500

@hazard_bp.route('/api/hazard/<int:hazard_id>/upvote', methods=['POST'])
def upvote_hazard(hazard_id):
    """
    用路人按讚覆核路障 API（用以核實與防刷機制）。
    
    HTTP 方法: POST
    對應模板: 無 (純 API 路由，回傳 JSON)
    """
    try:
        updated = HazardReport.upvote(hazard_id)
        if updated:
            return jsonify({
                "status": "success",
                "hazard": {
                    "id": updated.id,
                    "latitude": updated.latitude,
                    "longitude": updated.longitude,
                    "hazard_type": updated.hazard_type,
                    "description": updated.description,
                    "votes": updated.votes,
                    "created_at": updated.created_at
                }
            })
        else:
            return jsonify({"status": "error", "message": "該路障不存在，無法覆核"}), 404
    except Exception as e:
        print(f"覆核路障失敗: {e}", file=sys.stderr)
        return jsonify({"status": "error", "message": "伺服器內部錯誤"}), 500
