import sqlite3
import math
from app.models.user_route import _get_connection

def distance_in_meters(lat1, lng1, lat2, lng2):
    """
    使用哈弗辛公式 (Haversine formula) 計算地球上兩點的經緯度大圓距離（公尺）。
    """
    R = 6371000.0  # 地球平均半徑，單位：公尺
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lng1)
    
    a = math.sin(delta_phi / 2.0)**2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

class IntersectionLimit:
    def __init__(self, id=None, intersection_name=None, need_two_stage_turn=1, 
                 latitude=None, longitude=None):
        self.id = id
        self.intersection_name = intersection_name
        self.need_two_stage_turn = need_two_stage_turn
        self.latitude = latitude
        self.longitude = longitude

    @classmethod
    def create(cls, intersection_name, need_two_stage_turn, latitude, longitude):
        """
        建立一筆新的路口待轉指示資料。
        """
        conn = None
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO intersection_limits (intersection_name, need_two_stage_turn, latitude, longitude)
                VALUES (?, ?, ?, ?)
            ''', (intersection_name, need_two_stage_turn, latitude, longitude))
            conn.commit()
            new_id = cursor.lastrowid
            return cls(id=new_id, intersection_name=intersection_name, 
                       need_two_stage_turn=need_two_stage_turn, 
                       latitude=latitude, longitude=longitude)
        except sqlite3.Error as e:
            print(f"Error in IntersectionLimit.create: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()

    @classmethod
    def get_all(cls):
        """
        取得所有路口待轉對照列表。
        """
        conn = None
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM intersection_limits')
            rows = cursor.fetchall()
            return [cls(**dict(row)) for row in rows]
        except sqlite3.Error as e:
            print(f"Error in IntersectionLimit.get_all: {e}")
            return []
        finally:
            if conn:
                conn.close()

    @classmethod
    def get_by_id(cls, limit_id):
        """
        透過 ID 取得特定路口設定。
        """
        conn = None
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM intersection_limits WHERE id = ?', (limit_id,))
            row = cursor.fetchone()
            if row:
                return cls(**dict(row))
            return None
        except sqlite3.Error as e:
            print(f"Error in IntersectionLimit.get_by_id: {e}")
            return None
        finally:
            if conn:
                conn.close()

    @classmethod
    def find_nearest(cls, lat, lng):
        """
        尋找距離指定 GPS 座標 (lat, lng) 最近的待轉路口。
        
        回傳:
            tuple: (IntersectionLimit, float) -> (最近的路口物件, 距離公尺)
                   若無路口資料則回傳 (None, float('inf'))
        """
        intersections = cls.get_all()
        if not intersections:
            return None, float('inf')

        nearest_intersection = None
        min_distance = float('inf')

        for item in intersections:
            dist = distance_in_meters(lat, lng, item.latitude, item.longitude)
            if dist < min_distance:
                min_distance = dist
                nearest_intersection = item

        return nearest_intersection, min_distance

    @classmethod
    def update(cls, limit_id, intersection_name=None, need_two_stage_turn=None, 
               latitude=None, longitude=None):
        """
        更新特定路口屬性欄位。
        """
        conn = None
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            fields = {
                "intersection_name": intersection_name,
                "need_two_stage_turn": need_two_stage_turn,
                "latitude": latitude,
                "longitude": longitude
            }
            
            for key, val in fields.items():
                if val is not None:
                    updates.append(f"{key} = ?")
                    params.append(val)
                    
            if not updates:
                return cls.get_by_id(limit_id)
                
            params.append(limit_id)
            query = f"UPDATE intersection_limits SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, tuple(params))
            conn.commit()
            return cls.get_by_id(limit_id)
        except sqlite3.Error as e:
            print(f"Error in IntersectionLimit.update: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()

    @classmethod
    def delete(cls, limit_id):
        """
        刪除特定路口。
        """
        conn = None
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM intersection_limits WHERE id = ?', (limit_id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error in IntersectionLimit.delete: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
