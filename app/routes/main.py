from flask import Blueprint, render_template, request, jsonify

# 定義 main 模組的 Blueprint
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """
    導航主頁 (地圖與待轉倒數儀表板)
    
    HTTP 方法: GET
    對應模板: app/templates/map.html (繼承 base.html)
    說明: 讀取 UserSettings 參數，渲染 Leaflet 地圖、車速顯示儀表板、待轉警示圖標與倒數公尺數顯示介面。
    """
    pass

@main_bp.route('/api/intersection/check', methods=['POST'])
def check_intersection():
    """
    查詢最近路口待轉規則 API
    
    HTTP 方法: POST
    對應模板: 無 (純 JSON 響應)
    輸入參數 (JSON):
        - latitude (float, 必填): 騎士當前所處緯度
        - longitude (float, 必填): 騎士當前所處經度
    說明: 接收經緯度座標，調用 IntersectionLimit.find_nearest 模型查詢最近的路口。
          若投影距離在 50 公尺內，則回傳該路口的兩段式轉彎規定與路口中心經緯度。
    """
    pass
