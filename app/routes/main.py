import json
import time
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
        - destination (str, 必填): 目的地的名稱或地址
        - avoid_conditions (str, 選填): 避開的條件字串（例如：「擁擠路段,危險路口」）
    處理邏輯:
        1. 接收 JSON 格式請求，並驗證必要參數 destination 是否存在。若無則回傳 400 Bad Request。
        2. 模擬路徑計算過程，依據 avoid_conditions 微調規劃好的路線座標，確保避開指定路段。
        3. 模擬 0.15 秒的運算延遲，確保整體回傳時間在 3 秒以內（非功能需求）。
    輸出結果:
        - 成功 (200 OK): 回傳成功狀態、目的地、已套用的避開條件與 JSON 序列化後的路線座標資料。
        - 失敗 (400): 回傳錯誤狀態與說明。
    """
    data = request.get_json() or {}
    destination = data.get('destination', '').strip()
    avoid_conditions = data.get('avoid_conditions', '').strip()

    if not destination:
        return jsonify({
            "status": "error",
            "message": "請輸入目的地"
        }), 400

    # 模擬計算延遲
    time.sleep(0.15)

    # 依據避開條件生成不同的模擬路線座標資料
    # 預設路線 (起點模擬為台北車站 [121.5173, 25.0479])
    if "擁擠路段" in avoid_conditions and "危險路口" in avoid_conditions:
        # 同時避開兩者，走安全但稍遠的外環替代路線
        coordinates = [
            [121.5173, 25.0479],  # 台北車站
            [121.5230, 25.0510],
            [121.5310, 25.0520],
            [121.5430, 25.0450],
            [121.5645, 25.0338]   # 台北 101 (示意目的地)
        ]
        route_desc = "已成功避開擁擠路段與危險路口，為您規劃安全替代道路。"
    elif "擁擠路段" in avoid_conditions:
        # 僅避開擁擠路段，改走巷弄
        coordinates = [
            [121.5173, 25.0479],
            [121.5200, 25.0420],
            [121.5350, 25.0380],
            [121.5520, 25.0360],
            [121.5645, 25.0338]
        ]
        route_desc = "已成功避開擁擠路段，改由巷弄與次要道路導航。"
    elif "危險路口" in avoid_conditions:
        # 僅避開危險路口
        coordinates = [
            [121.5173, 25.0479],
            [121.5280, 25.0480],
            [121.5450, 25.0410],
            [121.5580, 25.0350],
            [121.5645, 25.0338]
        ]
        route_desc = "已成功繞開易發生事故之危險路口。"
    else:
        # 最短直達路線 (可能經過擁擠路段與危險路口)
        coordinates = [
            [121.5173, 25.0479],
            [121.5350, 25.0430],
            [121.5645, 25.0338]
        ]
        route_desc = "規劃最快直達路線。"

    # 將座標與說明序列化為 JSON 字串，以符合加密與儲存要求
    route_data_json = json.dumps({
        "coordinates": coordinates,
        "description": route_desc
    }, ensure_ascii=False)

    return jsonify({
        "status": "success",
        "destination": destination,
        "avoid_conditions": avoid_conditions,
        "route_data": route_data_json
    }), 200
