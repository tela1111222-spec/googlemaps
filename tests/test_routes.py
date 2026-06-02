# tests/test_routes.py
import unittest
import json
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, init_db
from app.models.user_settings import UserSettings
from app.models.intersection import IntersectionLimit

class TestRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        db_path = 'instance/database.db'
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except Exception:
                pass
        init_db()
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def test_get_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SPEED ALERTER', response.data)

    def test_get_settings(self):
        response = self.client.get('/settings')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'settings', response.data)

    def test_post_settings_success(self):
        response = self.client.post('/settings', data={
            'warning_threshold': '70',
            'enable_voice_alert': '1',
            'enable_auto_brightness': '1'
        })
        self.assertEqual(response.status_code, 302)
        
        # 驗證資料庫是否已更新
        settings = UserSettings.get_settings()
        self.assertEqual(settings.warning_threshold, 70)
        self.assertEqual(settings.enable_voice_alert, 1)
        self.assertEqual(settings.enable_auto_brightness, 1)

    def test_post_settings_invalid_range(self):
        response = self.client.post('/settings', data={
            'warning_threshold': '500', # 預期超出 10 - 100m 範圍
            'enable_voice_alert': '1',
            'enable_auto_brightness': '1'
        })
        self.assertEqual(response.status_code, 302)
        # 驗證資料庫設定沒有被更新為非法值 500
        settings = UserSettings.get_settings()
        self.assertNotEqual(settings.warning_threshold, 500)

    def test_api_check_intersection_match(self):
        # 忠孝新生路口 (25.042, 121.535) - 極接近
        response = self.client.post('/api/intersection/check',
            data=json.dumps({'latitude': 25.04201, 'longitude': 121.53501}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['status'], 'success')
        self.assertTrue(data['match'])
        self.assertEqual(data['intersection_name'], '忠孝新生路口 (忠孝新生捷運站旁)')
        self.assertEqual(data['need_two_stage_turn'], 1)
        self.assertLess(data['distance'], 5.0)

    def test_api_check_intersection_no_match(self):
        # 遠離所有待轉路口 (>50公尺)
        response = self.client.post('/api/intersection/check',
            data=json.dumps({'latitude': 25.0435, 'longitude': 121.5350}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['status'], 'success')
        self.assertFalse(data['match'])

if __name__ == '__main__':
    unittest.main()
