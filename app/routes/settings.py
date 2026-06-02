from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.user_settings import UserSettings

# 定義 settings 模組的 Blueprint
settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings')
def view_settings():
    """
    偏好設定頁面
    
    HTTP 方法: GET
    對應模板: app/templates/settings.html (繼承 base.html)
    說明: 獲取當前使用者的待轉與亮度警示設定參數，並渲染至設定頁面表單。
    """
    settings = UserSettings.get_settings()
    return render_template('settings.html', settings=settings)

@settings_bp.route('/settings', methods=['POST'])
def update_settings():
    """
    更新偏好設定
    
    HTTP 方法: POST
    對應模板: 無 (儲存成功後重導向)
    輸入參數 (Form Data):
        - warning_threshold (int, 必填): 預警距離門檻 (如 30, 50, 70 公尺)
        - enable_voice_alert (int, 選填): 語音提示開關 (複選框未勾選則預設為 0)
        - enable_auto_brightness (int, 選填): 自動亮度降亮開關 (複選框未勾選則預設為 0)
    說明: 接收表單提交資料並進行驗證，調用 UserSettings.update_settings() 更新資料庫後重導向回設定頁面。
    """
    try:
        warning_threshold_raw = request.form.get('warning_threshold')
        enable_voice_alert_raw = request.form.get('enable_voice_alert', '0')
        enable_auto_brightness_raw = request.form.get('enable_auto_brightness', '0')
        
        # 基本欄位驗證
        if warning_threshold_raw is None:
            flash("儲存失敗：預警距離欄位缺失！", "danger")
            return redirect(url_for('settings.view_settings'))
            
        warning_threshold = int(warning_threshold_raw)
        enable_voice_alert = int(enable_voice_alert_raw)
        enable_auto_brightness = int(enable_auto_brightness_raw)
        
        # 邊界值驗證
        if warning_threshold < 10 or warning_threshold > 100:
            flash("儲存失敗：預警距離範圍必須在 10 到 100 公尺之間！", "danger")
            return redirect(url_for('settings.view_settings'))
            
        # 更新資料庫
        UserSettings.update_settings(warning_threshold, enable_voice_alert, enable_auto_brightness)
        flash("偏好設定已成功儲存！", "success")
        
    except ValueError:
        flash("儲存失敗：輸入資料的格式不正確！", "danger")
    except Exception as e:
        flash(f"儲存失敗：發生系統錯誤 ({e})", "danger")
        
    return redirect(url_for('settings.view_settings'))
