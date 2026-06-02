import sqlite3
from app.models.user_route import _get_connection

class UserSettings:
    def __init__(self, id=None, warning_threshold=50, enable_voice_alert=1, enable_auto_brightness=1):
        self.id = id
        self.warning_threshold = warning_threshold
        self.enable_voice_alert = enable_voice_alert
        self.enable_auto_brightness = enable_auto_brightness

    @classmethod
    def get_settings(cls):
        """
        取得使用者設定。如果資料庫中沒有設定，則建立一筆預設設定。
        
        回傳:
            UserSettings: 使用者設定實體。
        """
        conn = None
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM user_settings LIMIT 1')
            row = cursor.fetchone()
            if row:
                return cls(**dict(row))
            else:
                # 建立預設設定
                cursor.execute('''
                    INSERT INTO user_settings (warning_threshold, enable_voice_alert, enable_auto_brightness)
                    VALUES (?, ?, ?)
                ''', (50, 1, 1))
                conn.commit()
                new_id = cursor.lastrowid
                return cls(id=new_id, warning_threshold=50, enable_voice_alert=1, enable_auto_brightness=1)
        except sqlite3.Error as e:
            print(f"Error in UserSettings.get_settings: {e}")
            # 回傳預設值，避免程式當掉
            return cls(id=1, warning_threshold=50, enable_voice_alert=1, enable_auto_brightness=1)
        finally:
            if conn:
                conn.close()

    @classmethod
    def update_settings(cls, warning_threshold: int, enable_voice_alert: int, enable_auto_brightness: int):
        """
        更新全域唯一的使用者設定。
        
        回傳:
            UserSettings: 更新後的使用者設定實體。
        """
        conn = None
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            # 先確認是否有資料
            cursor.execute('SELECT id FROM user_settings LIMIT 1')
            row = cursor.fetchone()
            if row:
                settings_id = row['id']
                cursor.execute('''
                    UPDATE user_settings
                    SET warning_threshold = ?, enable_voice_alert = ?, enable_auto_brightness = ?
                    WHERE id = ?
                ''', (warning_threshold, enable_voice_alert, enable_auto_brightness, settings_id))
            else:
                cursor.execute('''
                    INSERT INTO user_settings (warning_threshold, enable_voice_alert, enable_auto_brightness)
                    VALUES (?, ?, ?)
                ''', (warning_threshold, enable_voice_alert, enable_auto_brightness))
            conn.commit()
            return cls.get_settings()
        except sqlite3.Error as e:
            print(f"Error in UserSettings.update_settings: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()

    # --- 以下為符合 db-design skill 之標準 CRUD 方法 ---

    @classmethod
    def create(cls, warning_threshold=50, enable_voice_alert=1, enable_auto_brightness=1):
        """建立一筆新設定"""
        conn = None
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO user_settings (warning_threshold, enable_voice_alert, enable_auto_brightness)
                VALUES (?, ?, ?)
            ''', (warning_threshold, enable_voice_alert, enable_auto_brightness))
            conn.commit()
            new_id = cursor.lastrowid
            return cls(id=new_id, warning_threshold=warning_threshold, enable_voice_alert=enable_voice_alert, enable_auto_brightness=enable_auto_brightness)
        except sqlite3.Error as e:
            print(f"Error in UserSettings.create: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()

    @classmethod
    def get_by_id(cls, settings_id):
        """透過 ID 取得特定設定"""
        conn = None
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM user_settings WHERE id = ?', (settings_id,))
            row = cursor.fetchone()
            if row:
                return cls(**dict(row))
            return None
        except sqlite3.Error as e:
            print(f"Error in UserSettings.get_by_id: {e}")
            return None
        finally:
            if conn:
                conn.close()

    @classmethod
    def get_all(cls):
        """取得所有設定列表"""
        conn = None
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM user_settings')
            rows = cursor.fetchall()
            return [cls(**dict(row)) for row in rows]
        except sqlite3.Error as e:
            print(f"Error in UserSettings.get_all: {e}")
            return []
        finally:
            if conn:
                conn.close()

    @classmethod
    def update(cls, settings_id, warning_threshold=None, enable_voice_alert=None, enable_auto_brightness=None):
        """依據 ID 更新特定欄位"""
        conn = None
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            
            updates = []
            params = []
            if warning_threshold is not None:
                updates.append("warning_threshold = ?")
                params.append(warning_threshold)
            if enable_voice_alert is not None:
                updates.append("enable_voice_alert = ?")
                params.append(enable_voice_alert)
            if enable_auto_brightness is not None:
                updates.append("enable_auto_brightness = ?")
                params.append(enable_auto_brightness)
                
            if not updates:
                return cls.get_by_id(settings_id)
                
            params.append(settings_id)
            query = f"UPDATE user_settings SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, tuple(params))
            conn.commit()
            return cls.get_by_id(settings_id)
        except sqlite3.Error as e:
            print(f"Error in UserSettings.update: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()

    @classmethod
    def delete(cls, settings_id):
        """刪除設定"""
        conn = None
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM user_settings WHERE id = ?', (settings_id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error in UserSettings.delete: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
