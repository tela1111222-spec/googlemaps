from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.user_route import RouteHistory

# 定義 history 模組的 Blueprint
history_bp = Blueprint('history', __name__)

@history_bp.route('/history', methods=['GET'])
def list_history():
    """
    查看歷史行程列表頁面。
    
    HTTP 方法: GET
    對應模板: app/templates/history.html
    輸入參數: 無
    處理邏輯:
        1. 呼叫 `RouteHistory.get_all()` 查詢資料庫中所有的行程記錄。
        2. `RouteHistory` Model 會自動解密資料庫中 `encrypted_route_data` 欄位的加密資料，在 `route_data` 屬性中提供解密後的明文。
        3. 渲染並回傳 history.html，將行程列表傳入模板。
    """
    pass

@history_bp.route('/history', methods=['POST'])
def save_history():
    """
    建立一筆新的歷史行程記錄。
    
    HTTP 方法: POST
    對應模板: 無 (儲存成功後重導向)
    輸入參數 (Form Data):
        - destination (str, 必填): 目的地名稱或地址
        - avoid_conditions (str, 選填): 避開條件字串 (例如：「擁擠路段,危險路口」)
        - route_data (str, 必填): 路線地圖座標及導航資料 (明文 JSON 字串)
    處理邏輯:
        1. 從表單讀取 parameters 並驗證必填欄位 destination 與 route_data。
        2. 呼叫 `RouteHistory.create(destination, avoid_conditions, route_data)` 進行寫入。
           - 寫入時，Model 會在底層自動將 `route_data` 加密後存入 `encrypted_route_data` 欄位以保護個人隱私。
        3. 儲存成功後，使用 redirect 重導向至歷史紀錄列表頁面 `/history`。
    """
    pass

@history_bp.route('/history/<int:history_id>/delete', methods=['POST'])
def delete_history(history_id):
    """
    刪除指定的歷史行程記錄。
    
    HTTP 方法: POST
    對應模板: 無 (刪除成功後重導向)
    輸入參數 (URL):
        - history_id (int, 必填): 行程記錄的唯一識別 ID
    處理邏輯:
        1. 呼叫 `RouteHistory.delete(history_id)` 將對應記錄從資料庫刪除。
        2. 刪除完成後，重導向至歷史紀錄列表頁面 `/history`。
    """
    pass
