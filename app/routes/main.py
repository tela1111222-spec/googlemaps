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
    pass

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
        2. 呼叫路徑計算模組，依據 avoid_conditions 過濾出最佳騎乘路線。
        3. 優化演算法，確保回傳時間在 3 秒以內。
    輸出結果:
        - 成功 (200 OK): 回傳狀態、目的地、避開條件以及規劃好的路線座標資料。
        - 失敗 (400/500): 回傳錯誤狀態與錯誤描述訊息。
    """
    pass
