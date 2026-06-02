import sqlite3
from datetime import datetime

DATABASE_PATH = 'instance/database.db'

def _get_connection():
    """取得資料庫連線並設定 row_factory，以便用 dict 形式存取欄位"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

class SpeedCamera:
    def __init__(self, id=None, latitude=None, longitude=None, speed_limit=None, description=None, created_at=None):
        self.id = id
        self.latitude = latitude
        self.longitude = longitude
        self.speed_limit = speed_limit
        self.description = description
        self.created_at = created_at

    @classmethod
    def create(cls, latitude: float, longitude: float, speed_limit: int, description: str = None):
        """新增一個測速照相警告點"""
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO speed_camera (latitude, longitude, speed_limit, description)
            VALUES (?, ?, ?, ?)
        ''', (latitude, longitude, speed_limit, description))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        
        return cls.get_by_id(new_id)

    @classmethod
    def get_all(cls):
        """取得所有測速照相點"""
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM speed_camera ORDER BY created_at DESC')
        rows = cursor.fetchall()
        conn.close()
        
        return [cls(**dict(row)) for row in rows]

    @classmethod
    def get_by_id(cls, camera_id: int):
        """透過 ID 取得特定測速照相點"""
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM speed_camera WHERE id = ?', (camera_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return cls(**dict(row))
        return None

    @classmethod
    def get_nearby(cls, lat: float, lng: float, radius_degree: float = 0.005):
        """
        空間查詢優化 (Bounding Box)：高效率篩選出當前 GPS 座標周邊指定經緯度範圍 (預設 500m ≈ 0.005 度) 的測速相機
        滿足超速即時警示的 500ms 高效能響應要求
        """
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM speed_camera
            WHERE latitude BETWEEN ? AND ?
              AND longitude BETWEEN ? AND ?
        ''', (lat - radius_degree, lat + radius_degree, lng - radius_degree, lng + radius_degree))
        rows = cursor.fetchall()
        conn.close()
        
        return [cls(**dict(row)) for row in rows]

    @classmethod
    def update(cls, camera_id: int, latitude: float = None, longitude: float = None, speed_limit: int = None, description: str = None):
        """更新特定測速照相資訊"""
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
        if speed_limit is not None:
            updates.append("speed_limit = ?")
            params.append(speed_limit)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
            
        if not updates:
            conn.close()
            return cls.get_by_id(camera_id)
            
        params.append(camera_id)
        query = f"UPDATE speed_camera SET {', '.join(updates)} WHERE id = ?"
        
        cursor.execute(query, tuple(params))
        conn.commit()
        conn.close()
        
        return cls.get_by_id(camera_id)

    @classmethod
    def delete(cls, camera_id: int):
        """刪除特定測速照相點"""
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM speed_camera WHERE id = ?', (camera_id,))
        conn.commit()
        conn.close()
