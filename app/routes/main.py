from flask import Blueprint

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
    pass

@main_bp.route('/api/speed-limit', methods=['POST'])
def get_speed_limit():
    """
    查詢當前路段速限 API
    
    HTTP 方法: POST
    對應模板: 無 (純 JSON 響應)
    輸入參數 (JSON):
        - latitude (float, 必填): 騎士當前所處緯度
        - longitude (float, 必填): 騎士當前所處經度
    說明: 接收經緯度座標，調用 RoadSpeedLimit 模型查詢最近的路段並回傳其法定最高速限。
    """
    pass

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
    pass
