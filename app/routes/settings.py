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
    說明: 獲取當前騎士的警示偏好設定，並渲染至設定頁面表單。
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
        - warning_threshold (int, 必填): 容許超速值
        - enable_voice_alert (int, 選填): 語音/警示聲開關 (複選框若未勾選則不會傳送，此處預設為 0)
        - approaching_alert_ratio (float, 必填): 接近速限警告比例
    說明: 接收表單提交資料並進行驗證，調用 UserSettings.update_settings() 更新資料庫後重導向回設定頁面。
    """
    try:
        # 表單資料讀取，當 checkbox 未勾選時 request.form.get 會回傳 None，故預設給 '0'
        warning_threshold_raw = request.form.get('warning_threshold')
        enable_voice_alert_raw = request.form.get('enable_voice_alert', '0')
        approaching_alert_ratio_raw = request.form.get('approaching_alert_ratio')
        
        # 基本欄位驗證
        if warning_threshold_raw is None or approaching_alert_ratio_raw is None:
            flash("儲存失敗：欄位資料缺失！", "danger")
            return redirect(url_for('settings.view_settings'))
            
        # 型別轉換與範圍驗證
        warning_threshold = int(warning_threshold_raw)
        enable_voice_alert = int(enable_voice_alert_raw)
        approaching_alert_ratio = float(approaching_alert_ratio_raw)
        
        if warning_threshold < 0 or warning_threshold > 50:
            flash("儲存失敗：超速門檻數值必須在 0 到 50 公里之間！", "danger")
            return redirect(url_for('settings.view_settings'))
            
        if approaching_alert_ratio < 0.5 or approaching_alert_ratio > 1.0:
            flash("儲存失敗：接近警告比例必須在 50% 到 100% 之間！", "danger")
            return redirect(url_for('settings.view_settings'))
            
        # 更新設定
        UserSettings.update_settings(warning_threshold, enable_voice_alert, approaching_alert_ratio)
        flash("偏好設定已成功儲存！", "success")
        
    except ValueError:
        flash("儲存失敗：輸入的資料數值格式不正確！", "danger")
    except Exception as e:
        flash(f"儲存失敗：發生系統錯誤 ({e})", "danger")
        
    return redirect(url_for('settings.view_settings'))
