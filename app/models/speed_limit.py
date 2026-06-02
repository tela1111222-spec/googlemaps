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

def point_to_segment_projection(py, px, ay, ax, by, bx):
    """
    計算點 P(py, px) 在線段 AB 上的投影點 C(cy, cx)。
    A 與 B 是線段的端點座標。
    """
    dx = bx - ax
    dy = by - ay
    if dx == 0 and dy == 0:
        return ay, ax
        
    # 計算投影比例係數 t，並限制在 [0, 1] 之間以確保投影點落在線段內
    t = ((px - ax) * dx + (py - ay) * dy) / (dx*dx + dy*dy)
    t = max(0.0, min(1.0, t))
    
    cx = ax + t * dx
    cy = ay + t * dy
    return cy, cx

class RoadSpeedLimit:
    def __init__(self, id=None, road_name=None, speed_limit=None, 
                 start_lat=None, start_lng=None, end_lat=None, end_lng=None, 
                 upcoming_limit=None, upcoming_lat=None, upcoming_lng=None):
        self.id = id
        self.road_name = road_name
        self.speed_limit = speed_limit
        self.start_lat = start_lat
        self.start_lng = start_lng
        self.end_lat = end_lat
        self.end_lng = end_lng
        self.upcoming_limit = upcoming_limit
        self.upcoming_lat = upcoming_lat
        self.upcoming_lng = upcoming_lng

    @classmethod
    def create(cls, road_name, speed_limit, start_lat, start_lng, end_lat, end_lng, 
               upcoming_limit=None, upcoming_lat=None, upcoming_lng=None):
        """
        建立一筆新的道路速限區段資料。
        """
        conn = None
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO road_limits (road_name, speed_limit, start_lat, start_lng, end_lat, end_lng, 
                                         upcoming_limit, upcoming_lat, upcoming_lng)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (road_name, speed_limit, start_lat, start_lng, end_lat, end_lng, 
                  upcoming_limit, upcoming_lat, upcoming_lng))
            conn.commit()
            new_id = cursor.lastrowid
            return cls(id=new_id, road_name=road_name, speed_limit=speed_limit, 
                       start_lat=start_lat, start_lng=start_lng, end_lat=end_lat, end_lng=end_lng, 
                       upcoming_limit=upcoming_limit, upcoming_lat=upcoming_lat, upcoming_lng=upcoming_lng)
        except sqlite3.Error as e:
            print(f"Error in RoadSpeedLimit.create: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()

    @classmethod
    def get_all(cls):
        """
        取得所有道路速限區段列表。
        """
        conn = None
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM road_limits')
            rows = cursor.fetchall()
            return [cls(**dict(row)) for row in rows]
        except sqlite3.Error as e:
            print(f"Error in RoadSpeedLimit.get_all: {e}")
            return []
        finally:
            if conn:
                conn.close()

    @classmethod
    def get_by_id(cls, road_id):
        """
        透過 ID 取得特定道路速限區段。
        """
        conn = None
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM road_limits WHERE id = ?', (road_id,))
            row = cursor.fetchone()
            if row:
                return cls(**dict(row))
            return None
        except sqlite3.Error as e:
            print(f"Error in RoadSpeedLimit.get_by_id: {e}")
            return None
        finally:
            if conn:
                conn.close()

    @classmethod
    def find_nearest(cls, lat, lng):
        """
        尋找距離指定 GPS 座標 (lat, lng) 最近的道路段。
        
        回傳:
            tuple: (RoadSpeedLimit, float) -> (最近的道路物件, 距離公尺)
                   若無道路資料則回傳 (None, float('inf'))
        """
        roads = cls.get_all()
        if not roads:
            return None, float('inf')

        nearest_road = None
        min_distance = float('inf')

        for road in roads:
            # 計算點到線段的投影點
            cy, cx = point_to_segment_projection(
                lat, lng, 
                road.start_lat, road.start_lng, 
                road.end_lat, road.end_lng
            )
            # 計算點到投影點的真實大圓距離（公尺）
            dist = distance_in_meters(lat, lng, cy, cx)
            if dist < min_distance:
                min_distance = dist
                nearest_road = road

        return nearest_road, min_distance

    @classmethod
    def update(cls, road_id, road_name=None, speed_limit=None, 
               start_lat=None, start_lng=None, end_lat=None, end_lng=None, 
               upcoming_limit=None, upcoming_lat=None, upcoming_lng=None):
        """
        更新特定道路速限欄位資料。
        """
        conn = None
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            fields = {
                "road_name": road_name,
                "speed_limit": speed_limit,
                "start_lat": start_lat,
                "start_lng": start_lng,
                "end_lat": end_lat,
                "end_lng": end_lng,
                "upcoming_limit": upcoming_limit,
                "upcoming_lat": upcoming_lat,
                "upcoming_lng": upcoming_lng
            }
            
            for key, val in fields.items():
                if val is not None:
                    updates.append(f"{key} = ?")
                    params.append(val)
                    
            if not updates:
                return cls.get_by_id(road_id)
                
            params.append(road_id)
            query = f"UPDATE road_limits SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, tuple(params))
            conn.commit()
            return cls.get_by_id(road_id)
        except sqlite3.Error as e:
            print(f"Error in RoadSpeedLimit.update: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()

    @classmethod
    def delete(cls, road_id):
        """
        刪除特定道路速限區段。
        """
        conn = None
        try:
            conn = _get_connection()
            cursor = conn.cursor()
            cursor.execute('DELETE FROM road_limits WHERE id = ?', (road_id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error in RoadSpeedLimit.delete: {e}")
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()
