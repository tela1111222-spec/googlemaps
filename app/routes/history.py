from flask import Blueprint, render_template, request, redirect, url_for, flash
import sys
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
    try:
        histories = RouteHistory.get_all()
        return render_template('history.html', histories=histories)
    except Exception as e:
        print(f"載入歷史行程列表失敗: {e}", file=sys.stderr)
        flash("載入歷史行程失敗，請稍後再試！", "danger")
        return render_template('history.html', histories=[])

@history_bp.route('/history', methods=['POST'])
def save_history():
    """
    建立一筆新的歷史行程記錄。
    
    HTTP 方法: POST
    對應模板: 無 (儲存成功後重導向)
    輸入參數 (Form Data 或 JSON):
        - destination (str, 必填): 目的地名稱或地址
        - avoid_conditions (str, 選填): 避開條件字串 (例如：「擁擠路段,危險路口」)
        - route_data (str, 必填): 路線地圖座標及導航資料 (明文 JSON 字串)
    處理邏輯:
        1. 從表單讀取 parameters 並驗證必填欄位 destination 與 route_data。
        2. 呼叫 `RouteHistory.create(destination, avoid_conditions, route_data)` 進行寫入。
           - 寫入時，Model 會在底層自動將 `route_data` 加密後存入 `encrypted_route_data` 欄位以保護個人隱私。
        3. 儲存成功後，使用 redirect 重導向至歷史紀錄列表頁面 `/history`。
    """
    # 支援 JSON 與 Form Data 雙重格式以提高彈性
    if request.is_json:
        data = request.get_json()
        destination = data.get('destination')
        avoid_conditions = data.get('avoid_conditions', '')
        route_data = data.get('route_data')
    else:
        destination = request.form.get('destination')
        avoid_conditions = request.form.get('avoid_conditions', '')
        route_data = request.form.get('route_data')
        
    if not destination or not route_data:
        flash("儲存失敗！目的地與路線資料為必填欄位。", "danger")
        return redirect(url_for('history.list_history'))
        
    try:
        new_route = RouteHistory.create(destination, avoid_conditions, route_data)
        if new_route:
            flash("成功儲存本次行程軌跡！", "success")
        else:
            flash("儲存行程時發生錯誤，資料寫入失敗。", "danger")
    except Exception as e:
        print(f"儲存行程紀錄失敗: {e}", file=sys.stderr)
        flash("系統錯誤：無法儲存行程記錄。", "danger")
        
    return redirect(url_for('history.list_history'))

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
    try:
        success = RouteHistory.delete(history_id)
        if success:
            flash("已成功刪除該筆行程記錄！", "success")
        else:
            flash("刪除失敗，該行程記錄可能不存在。", "danger")
    except Exception as e:
        print(f"刪除行程記錄 {history_id} 失敗: {e}", file=sys.stderr)
        flash("系統錯誤：無法完成刪除操作。", "danger")
        
    return redirect(url_for('history.list_history'))
