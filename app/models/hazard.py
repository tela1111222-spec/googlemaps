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

class HazardReport:
    def __init__(self, id=None, latitude=None, longitude=None, hazard_type=None, description=None, votes=0, created_at=None):
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.hazard_type = hazard_type # 'accident' (車禍), 'construction' (施工), 'obstacle' (障礙物)
        self.description = description
        self.votes = votes
        self.created_at = created_at

    @classmethod
    def create(cls, latitude: float, longitude: float, hazard_type: str, description: str = None):
        """用路人一鍵回報突發路況與路障"""
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO hazard_report (latitude, longitude, hazard_type, description, votes)
                VALUES (?, ?, ?, ?, 0)
            ''', (latitude, longitude, hazard_type, description))
            conn.commit()
            new_id = cursor.lastrowid
            conn.close()
            
            return cls.get_by_id(new_id)
        except sqlite3.Error as e:
            print(f"建立路障回報失敗: {e}", file=sys.stderr)
            return None

    @classmethod
    def get_all(cls):
        """取得所有即時路況回報，依時間由新到舊排序"""
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM hazard_report ORDER BY created_at DESC')
            rows = cursor.fetchall()
            conn.close()
            
            return [cls(**dict(row)) for row in rows]
        except sqlite3.Error as e:
            print(f"取得所有路障回報失敗: {e}", file=sys.stderr)
            return []

    @classmethod
    def get_by_id(cls, hazard_id: int):
        """透過 ID 取得特定路障資訊"""
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM hazard_report WHERE id = ?', (hazard_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return cls(**dict(row))
            return None
        except sqlite3.Error as e:
            print(f"透過 ID 取得路障回報失敗: {e}", file=sys.stderr)
            return None

    @classmethod
    def get_nearby(cls, lat: float, lng: float, radius_degree: float = 0.05):
        """
        空間查詢優化 (Bounding Box)：篩選出特定範圍 (預設 5km ≈ 0.05 度) 的即時路況與障礙回報
        用於在地圖上標記周邊路況，以利動態重新規劃避開路障
        """
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM hazard_report
                WHERE latitude BETWEEN ? AND ?
                  AND longitude BETWEEN ? AND ?
                ORDER BY created_at DESC
            ''', (lat - radius_degree, lat + radius_degree, lng - radius_degree, lng + radius_degree))
            rows = cursor.fetchall()
            conn.close()
            
            return [cls(**dict(row)) for row in rows]
        except sqlite3.Error as e:
            print(f"空間檢索路障失敗: {e}", file=sys.stderr)
            return []

    @classmethod
    def upvote(cls, hazard_id: int):
        """用路人點擊覆核 (讚)，提升該回報的可信度"""
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE hazard_report
                SET votes = votes + 1
                WHERE id = ?
            ''', (hazard_id,))
            conn.commit()
            conn.close()
            
            return cls.get_by_id(hazard_id)
        except sqlite3.Error as e:
            print(f"覆核路障回報失敗: {e}", file=sys.stderr)
            return None

    @classmethod
    def update(cls, hazard_id: int, latitude: float = None, longitude: float = None, hazard_type: str = None, description: str = None, votes: int = None):
        """更新特定路況回報資訊"""
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
            if hazard_type is not None:
                updates.append("hazard_type = ?")
                params.append(hazard_type)
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            if votes is not None:
                updates.append("votes = ?")
                params.append(votes)
                
            if not updates:
                conn.close()
                return cls.get_by_id(hazard_id)
                
            params.append(hazard_id)
            query = f"UPDATE hazard_report SET {', '.join(updates)} WHERE id = ?"
            
            cursor.execute(query, tuple(params))
            conn.commit()
            conn.close()
            
            return cls.get_by_id(hazard_id)
        except sqlite3.Error as e:
            print(f"更新路障回報失敗: {e}", file=sys.stderr)
            return None

    @classmethod
    def delete(cls, hazard_id: int) -> bool:
        """刪除已排除的路障點或檢舉回報過期的路障"""
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM hazard_report WHERE id = ?', (hazard_id,))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"刪除路障回報失敗: {e}", file=sys.stderr)
            return False
