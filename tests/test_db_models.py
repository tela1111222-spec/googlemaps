# tests/test_db_models.py
import unittest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, init_db
from app.models.user_settings import UserSettings
from app.models.intersection import IntersectionLimit

class TestDatabaseModels(unittest.TestCase):
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

    def test_user_settings_crud(self):
        # 1. 讀取預設設定
        settings = UserSettings.get_settings()
        self.assertIsNotNone(settings)
        self.assertEqual(settings.warning_threshold, 50)
        self.assertEqual(settings.enable_voice_alert, 1)
        self.assertEqual(settings.enable_auto_brightness, 1)

        # 2. 更新設定
        updated = UserSettings.update_settings(30, 0, 0)
        self.assertIsNotNone(updated)
        self.assertEqual(updated.warning_threshold, 30)
        self.assertEqual(updated.enable_voice_alert, 0)
        self.assertEqual(updated.enable_auto_brightness, 0)

        # 還原預設
        UserSettings.update_settings(50, 1, 1)

    def test_intersection_limit_crud(self):
        # 1. 建立測試路口
        item = IntersectionLimit.create("測試路口A", 1, 25.100, 121.500)
        self.assertIsNotNone(item)
        self.assertEqual(item.intersection_name, "測試路口A")
        
        # 2. 獲取所有路口
        all_items = IntersectionLimit.get_all()
        self.assertTrue(len(all_items) >= 4) # 3 mock + 1 new

        # 3. 藉由 ID 獲取
        fetched = IntersectionLimit.get_by_id(item.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.intersection_name, "測試路口A")

        # 4. 更新路口
        updated = IntersectionLimit.update(item.id, intersection_name="測試路口A_更新", need_two_stage_turn=0)
        self.assertIsNotNone(updated)
        self.assertEqual(updated.intersection_name, "測試路口A_更新")
        self.assertEqual(updated.need_two_stage_turn, 0)

        # 5. 測試 find_nearest 幾何比對
        # 查詢點與 (25.100, 121.500) 極近
        nearest, dist = IntersectionLimit.find_nearest(25.10005, 121.50005)
        self.assertEqual(nearest.id, item.id)
        self.assertLess(dist, 15.0) # 距離應小於 15 公尺

        # 6. 刪除路口
        success = IntersectionLimit.delete(item.id)
        self.assertTrue(success)
        self.assertIsNone(IntersectionLimit.get_by_id(item.id))

if __name__ == '__main__':
    unittest.main()
