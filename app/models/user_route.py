import sqlite3
import base64
from datetime import datetime

# 對應系統架構設計的資料庫路徑
DATABASE_PATH = 'instance/database.db'

def _get_connection():
    """
    取得資料庫連線並設定 row_factory，以便用 dict 形式存取欄位。
    
    回傳:
        sqlite3.Connection: 資料庫連線實體。
    
    例外:
        sqlite3.Error: 當資料庫連線失敗時拋出。
    """
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection failed: {e}")
        raise

# 簡易的加解密機制 (為滿足 PRD 的加密儲存需求)
# 實務上建議使用 cryptography 等套件進行更安全的 AES/Fernet 加密
def encrypt_data(data: str) -> str:
    """將路線資料加密（目前使用 base64 進行簡單編碼示範）"""
    return base64.b64encode(data.encode('utf-8')).decode('utf-8')

def decrypt_data(encrypted_data: str) -> str:
    """將路線資料解密還原"""
    return base64.b64decode(encrypted_data.encode('utf-8')).decode('utf-8')

class RouteHistory:
    def __init__(self, id=None, destination=None, avoid_conditions=None, encrypted_route_data=None, created_at=None):
        self.id = id
        self.destination = destination
        self.avoid_conditions = avoid_conditions
        self.encrypted_route_data = encrypted_route_data
        self.created_at = created_at

    @property
    def route_data(self):
        """屬性方法：讀取時自動解密，回傳原始路線資料"""
        if self.encrypted_route_data:
            try:
                return decrypt_data(self.encrypted_route_data)
            except Exception as e:
                print(f"Error decrypting route data for record ID {self.id}: {e}")
                return None
        return None

    @classmethod
    def create(cls, destination: str, avoid_conditions: str, route_data: str):
        """
        建立一筆新行程紀錄，會將路線明文加密後儲存。
        
        參數:
            destination (str): 目的地名稱或地址。
            avoid_conditions (str): 使用者選擇的避開條件（如以逗號分隔的字串）。
            route_data (str): 路線座標等明文資料。
            
        回傳:
            RouteHistory: 建立成功後，回傳該筆行程紀錄的 RouteHistory 物件；若失敗則回傳 None。
        """
        encrypted_data = encrypt_data(route_data)
        conn = None
        new_id = None
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO route_history (destination, avoid_conditions, encrypted_route_data)
                VALUES (?, ?, ?)
            ''', (destination, avoid_conditions, encrypted_data))
            conn.commit()
            new_id = cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error in RouteHistory.create: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()
                
        if new_id:
            return cls.get_by_id(new_id)
        return None

    @classmethod
    def get_all(cls):
        """
        取得所有行程紀錄，依時間由新至舊排序。
        
        回傳:
            list: 包含所有 RouteHistory 實體的列表，若查詢失敗則回傳空列表。
        """
        conn = None
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM route_history ORDER BY created_at DESC')
            rows = cursor.fetchall()
            return [cls(**dict(row)) for row in rows]
        except sqlite3.Error as e:
            print(f"Error in RouteHistory.get_all: {e}")
            return []
        finally:
            if conn:
                conn.close()

    @classmethod
    def get_by_id(cls, history_id):
        """
        透過 ID 取得單筆行程紀錄。
        
        參數:
            history_id (int): 行程紀錄的 ID。
            
        回傳:
            RouteHistory: 取得的 RouteHistory 物件，若找不到或出錯則回傳 None。
        """
        conn = None
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM route_history WHERE id = ?', (history_id,))
            row = cursor.fetchone()
            if row:
                return cls(**dict(row))
            return None
        except sqlite3.Error as e:
            print(f"Error in RouteHistory.get_by_id for ID {history_id}: {e}")
            return None
        finally:
            if conn:
                conn.close()

    @classmethod
    def update(cls, history_id, destination=None, avoid_conditions=None):
        """
        更新行程資訊。
        
        參數:
            history_id (int): 行程紀錄的 ID。
            destination (str, 選填): 新的目的地名稱。
            avoid_conditions (str, 選填): 新的避開條件。
            
        回傳:
            RouteHistory: 更新後的 RouteHistory 物件，若更新失敗則回傳 None。
        """
        updates = []
        params = []
        if destination is not None:
            updates.append("destination = ?")
            params.append(destination)
        if avoid_conditions is not None:
            updates.append("avoid_conditions = ?")
            params.append(avoid_conditions)
            
        if not updates:
            return cls.get_by_id(history_id)
            
        params.append(history_id)
        query = f"UPDATE route_history SET {', '.join(updates)} WHERE id = ?"
        
        conn = None
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error in RouteHistory.update for ID {history_id}: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()
                
        return cls.get_by_id(history_id)

    @classmethod
    def delete(cls, history_id):
        """
        刪除單筆行程紀錄。
        
        參數:
            history_id (int): 行程紀錄的 ID。
            
        回傳:
            bool: 刪除成功回傳 True，若出錯或失敗則回傳 False。
        """
        conn = None
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM route_history WHERE id = ?', (history_id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error in RouteHistory.delete for ID {history_id}: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
