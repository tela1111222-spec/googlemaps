import sqlite3
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

class TwoStageTurn:
    def __init__(self, id=None, latitude=None, longitude=None, description=None, created_at=None):
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.description = description
        self.created_at = created_at

    @classmethod
    def create(cls, latitude: float, longitude: float, description: str = None):
        """新增一個需要兩段式待轉的路口提示點"""
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO two_stage_turn (latitude, longitude, description)
                VALUES (?, ?, ?)
            ''', (latitude, longitude, description))
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            
            return cls.get_by_id(new_id)
        except sqlite3.Error as e:
            print(f"建立待轉路口點失敗: {e}", file=sys.stderr)
            return None

    @classmethod
    def get_all(cls):
        """取得所有待轉路口資料"""
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM two_stage_turn ORDER BY created_at DESC')
            rows = cursor.fetchall()
            conn.close()
            
            return [cls(**dict(row)) for row in rows]
        except sqlite3.Error as e:
            print(f"取得所有待轉路口失敗: {e}", file=sys.stderr)
            return []

    @classmethod
    def get_by_id(cls, turn_id: int):
        """透過 ID 取得特定待轉路口資訊"""
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM two_stage_turn WHERE id = ?', (turn_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return cls(**dict(row))
            return None
        except sqlite3.Error as e:
            print(f"透過 ID 取得待轉路口失敗: {e}", file=sys.stderr)
            return None

    @classmethod
    def get_nearby(cls, lat: float, lng: float, radius_degree: float = 0.003):
        """
        空間查詢優化 (Bounding Box)：篩選出接近前方轉彎路口半徑 (預設約 300m ≈ 0.003 度) 的兩段式待轉指示警告點
        提供前端即時於畫面切換兩段式左轉圖示與播報
        """
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM two_stage_turn
                WHERE latitude BETWEEN ? AND ?
                  AND longitude BETWEEN ? AND ?
            ''', (lat - radius_degree, lat + radius_degree, lng - radius_degree, lng + radius_degree))
            rows = cursor.fetchall()
            conn.close()
            
            return [cls(**dict(row)) for row in rows]
        except sqlite3.Error as e:
            print(f"空間檢索待轉路口失敗: {e}", file=sys.stderr)
            return []

    @classmethod
    def update(cls, turn_id: int, latitude: float = None, longitude: float = None, description: str = None):
        """更新特定待轉路口資訊"""
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            
            updates = []
            params = []
            if latitude is not None:
                updates.append("latitude = ?")
                params.append(latitude)
            if longitude is not None:
                updates.append("longitude = ?")
                params.append(longitude)
            if description is not None:
                updates.append("description = ?")
                params.append(description)
                
            if not updates:
                conn.close()
                return cls.get_by_id(turn_id)
                
            params.append(turn_id)
            query = f"UPDATE two_stage_turn SET {', '.join(updates)} WHERE id = ?"
            
            cursor.execute(query, tuple(params))
            conn.commit()
            conn.close()
            
            return cls.get_by_id(turn_id)
        except sqlite3.Error as e:
            print(f"更新待轉路口失敗: {e}", file=sys.stderr)
            return None

    @classmethod
    def delete(cls, turn_id: int) -> bool:
        """刪除特定待轉路口點"""
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM two_stage_turn WHERE id = ?', (turn_id,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"刪除待轉路口失敗: {e}", file=sys.stderr)
            return False
