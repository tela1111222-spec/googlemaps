# tests/test_distance_threshold.py
import unittest
import json
import os
import sys

# 將專案根目錄加入 Python 模組搜尋路徑
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, init_db

class TestDistanceThreshold(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 確保資料庫初始化
        init_db()
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def test_speed_limit_matching_close(self):
        # 忠孝東路三段起點附近 (非常接近線段，距離應該近乎 0 公尺)
        response = self.client.post('/api/speed-limit', 
            data=json.dumps({'latitude': 25.042, 'longitude': 121.535}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['road_name'], '忠孝東路三段')
        self.assertEqual(data['speed_limit'], 50)
        self.assertLess(data['distance'], 5.0)

    def test_speed_limit_matching_far(self):
        # 距離忠孝東路三段 (25.042) 約 110 公尺的點 (25.043, 121.535)
        # 由於大於 50 公尺，預期應回退至「未知路段」與速限 50
        response = self.client.post('/api/speed-limit', 
            data=json.dumps({'latitude': 25.043, 'longitude': 121.535}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['road_name'], '未知路段')
        self.assertEqual(data['speed_limit'], 50)
        self.assertGreater(data['distance'], 50.0)

    def test_route_preview_close(self):
        # 位於忠孝東路三段且距離前方降速預告點 (25.042, 121.543) 約 200 公尺 (25.042, 121.541)
        response = self.client.post('/api/route/preview', 
            data=json.dumps({'latitude': 25.042, 'longitude': 121.541}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['status'], 'success')
        self.assertTrue(data['trigger_preview'])
        self.assertEqual(data['upcoming_limit'], 40)
        self.assertLess(data['distance_to_change'], 300.0)

    def test_route_preview_far_from_road(self):
        # 雖然距離降速預告點 (25.042, 121.543) 也是約 220 公尺，但偏離道路 110 公尺 (25.043, 121.541)
        # 預期不應觸發預告，因為已經偏離了匹配的道路 (dist > 50m)
        response = self.client.post('/api/route/preview', 
            data=json.dumps({'latitude': 25.043, 'longitude': 121.541}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['status'], 'success')
        self.assertFalse(data['trigger_preview'])

if __name__ == '__main__':
    unittest.main()
