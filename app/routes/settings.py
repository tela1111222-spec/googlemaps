from flask import Blueprint

# 定義 settings 模組的 Blueprint
settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings')
def view_settings():
    """
    偏好設定頁面
    
    HTTP 方法: GET
    對應模板: app/templates/settings.html (繼承 base.html)
    說明: 獲取當前騎士的警示偏好設定，並渲染至設定頁面表單。
    """
    pass

@settings_bp.route('/settings', methods=['POST'])
def update_settings():
    """
    更新偏好設定
    
    HTTP 方法: POST
    對應模板: 無 (儲存成功後重導向)
    輸入參數 (Form Data):
        - warning_threshold (int, 必填): 容許超速值
        - enable_voice_alert (int, 必填): 語音/警示聲開關
        - approaching_alert_ratio (float, 必填): 接近速限警告比例
    說明: 接收表單提交資料並進行驗證，調用 UserSettings.update_settings() 更新資料庫後重導向回設定頁面。
    """
    pass
