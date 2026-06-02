import sqlite3
import base64
import sys
from datetime import datetime

DATABASE_PATH = 'instance/database.db'

def _get_connection():
    """取得資料庫連線並設定 row_factory，以便用 dict 形式存取欄位"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"資料庫連線失敗: {e}", file=sys.stderr)
        raise

def encrypt_data(data: str) -> str:
    """將路線資料加密（目前使用 base64 進行簡單編碼示範）"""
    if not data:
        return ""
    try:
        return base64.b64encode(data.encode('utf-8')).decode('utf-8')
    except Exception as e:
        print(f"資料加密失敗: {e}", file=sys.stderr)
        return ""

def decrypt_data(encrypted_data: str) -> str:
    """將路線資料解密還原"""
    if not encrypted_data:
        return ""
    try:
        return base64.b64decode(encrypted_data.encode('utf-8')).decode('utf-8')
    except Exception as e:
        print(f"資料解密失敗: {e}", file=sys.stderr)
        return ""

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
            return decrypt_data(self.encrypted_route_data)
        return None

    @classmethod
    def create(cls, destination: str, avoid_conditions: str, route_data: str):
        """建立一筆新行程紀錄"""
        try:
            # 寫入前對路線資料進行加密
            encrypted_data = encrypt_data(route_data)
            
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO route_history (destination, avoid_conditions, encrypted_route_data)
                VALUES (?, ?, ?)
            ''', (destination, avoid_conditions, encrypted_data))
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            
            return cls.get_by_id(new_id)
        except sqlite3.Error as e:
            print(f"建立行程紀錄失敗: {e}", file=sys.stderr)
            return None

    @classmethod
    def get_all(cls):
        """取得所有行程紀錄，依時間由新至舊排序"""
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM route_history ORDER BY created_at DESC')
            rows = cursor.fetchall()
            conn.close()
            
            return [cls(**dict(row)) for row in rows]
        except sqlite3.Error as e:
            print(f"取得所有行程紀錄失敗: {e}", file=sys.stderr)
            return []

    @classmethod
    def get_by_id(cls, history_id: int):
        """透過 ID 取得單筆行程紀錄"""
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM route_history WHERE id = ?', (history_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return cls(**dict(row))
            return None
        except sqlite3.Error as e:
            print(f"透過 ID 取得行程紀錄失敗: {e}", file=sys.stderr)
            return None

    @classmethod
    def update(cls, history_id: int, destination=None, avoid_conditions=None):
        """更新行程資訊 (MVP 階段通常僅供更新目的地或避開條件)"""
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            
            updates = []
            params = []
            if destination is not None:
                updates.append("destination = ?")
                params.append(destination)
            if avoid_conditions is not None:
                updates.append("avoid_conditions = ?")
                params.append(avoid_conditions)
                
            if not updates:
                conn.close()
                return cls.get_by_id(history_id)
                
            params.append(history_id)
            query = f"UPDATE route_history SET {', '.join(updates)} WHERE id = ?"
            
            cursor.execute(query, tuple(params))
            conn.commit()
            conn.close()
            
            return cls.get_by_id(history_id)
        except sqlite3.Error as e:
            print(f"更新行程紀錄失敗: {e}", file=sys.stderr)
            return None

    @classmethod
    def delete(cls, history_id: int) -> bool:
        """刪除單筆行程紀錄"""
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM route_history WHERE id = ?', (history_id,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"刪除行程紀錄失敗: {e}", file=sys.stderr)
            return False
