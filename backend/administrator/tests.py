from django.test import TestCase, Client
from django.urls import reverse
from .models import Cafe, Administrator
import json

class AdminTestCase(TestCase):
    def setUp(self):
        # 建立測試用的 Administrator 和 Cafe 資料
        self.admin = Administrator.objects.create(uid="admin1")
        self.client = Client()

        # 設定測試用的 API 路徑
        self.add_cafe_url = reverse('addNewCafe')
        self.update_cafe_url = reverse('updateCafe')
        self.delete_cafe_url = reverse('deleteCafe')
        self.judge_cafe_url = reverse('judgeCafe')

        # 測試用的 Cafe 資料
        self.cafe_data = {
            "adminId": self.admin.uid,
            "name": "Test Cafe",
            "phone": "123456789",
            "addr": "123 Test Street",
            "quiet": 3,
            "grade": 4,
            "cafeTimeLimit": 120,
            "socket": True,
            "petsAllowed": False,
            "wiFi": True,
            "openHour": "08:00",
            "openNow": True,
            "distance": 500,
            "info": "A nice place to relax",
            "comment": "Great coffee",
            "igHashTagCnt": 150,
            "googleReviewCnt": 50,
            "IGLink": "https://instagram.com/test_cafe",
            "FBLink": "https://facebook.com/test_cafe",
            "googleReviewLink": "https://google.com/test_cafe"
        }

    def test_add_cafe_success(self):
        # 測試新增咖啡廳成功
        response = self.client.post(self.add_cafe_url, data=json.dumps(self.cafe_data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('success'))
        self.assertIn('CafeId', response.json())

    def test_add_cafe_missing_fields(self):
        # 測試新增咖啡廳時缺少必要欄位
        incomplete_data = self.cafe_data.copy()
        incomplete_data.pop('name')  # 移除必要欄位
        response = self.client.post(self.add_cafe_url, data=json.dumps(incomplete_data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json().get('success'))
        self.assertIn('缺少必要的參數', response.json().get('err'))

    def test_update_cafe_success(self):
        # 測試更新咖啡廳成功
        cafe = Cafe.objects.create(**self.cafe_data)
        update_data = {
            "cafeId": cafe.cafe_id,
            "name": "Updated Cafe Name"
        }
        response = self.client.put(self.update_cafe_url, data=json.dumps(update_data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('success'))
        self.assertEqual(Cafe.objects.get(cafe_id=cafe.cafe_id).name, "Updated Cafe Name")

    def test_update_cafe_not_found(self):
        # 測試更新不存在的咖啡廳
        update_data = {
            "cafeId": "nonexistent_id",
            "name": "Updated Cafe Name"
        }
        response = self.client.put(self.update_cafe_url, data=json.dumps(update_data), content_type="application/json")
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json().get('success'))
        self.assertIn('找不到指定的咖啡廳', response.json().get('err'))

    def test_delete_cafe_success(self):
        # 測試刪除咖啡廳成功
        cafe = Cafe.objects.create(**self.cafe_data)
        delete_data = {
            "adminId": self.admin.uid,
            "cafeId": cafe.cafe_id
        }
        response = self.client.post(self.delete_cafe_url, data=json.dumps(delete_data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('success'))
        self.assertFalse(Cafe.objects.filter(cafe_id=cafe.cafe_id).exists())

    def test_delete_cafe_not_found(self):
        # 測試刪除不存在的咖啡廳
        delete_data = {
            "adminId": self.admin.uid,
            "cafeId": "nonexistent_id"
        }
        response = self.client.post(self.delete_cafe_url, data=json.dumps(delete_data), content_type="application/json")
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.json().get('success'))
        self.assertIn('指定的咖啡廳不存在', response.json().get('err'))

    def test_judge_cafe_success(self):
        # 測試審核咖啡廳成功
        cafe = Cafe.objects.create(**self.cafe_data)
        judge_data = {
            "adminId": self.admin.uid,
            "cafeId": cafe.cafe_id,
            "isLegal": True
        }
        response = self.client.put(self.judge_cafe_url, data=json.dumps(judge_data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('success'))
        self.assertTrue(Cafe.objects.get(cafe_id=cafe.cafe_id).legal)

    def test_judge_cafe_missing_fields(self):
        # 測試審核咖啡廳時缺少必要欄位
        judge_data = {
            "adminId": self.admin.uid,
            "cafeId": "some_id"
        }
        response = self.client.put(self.judge_cafe_url, data=json.dumps(judge_data), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json().get('success'))
        self.assertIn('缺少必要的參數', response.json().get('err'))
