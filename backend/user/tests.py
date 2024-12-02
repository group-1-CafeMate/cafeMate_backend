from django.test import TestCase
from django.contrib.auth.hashers import make_password, check_password
from django.urls import reverse
from .models import Profile
import json

class ProfileTestCase(TestCase):
    def setUp(self):
        # 創建測試用的 Profile 實例
        self.user1 = Profile.objects.create(
            email='user1@example.com',
            username='user1',
            password=make_password('password123'),  # 密碼加密
        )
        self.user2 = Profile.objects.create(
            email='user2@example.com',
            username='user2',
            password=make_password('password321'),  # 密碼加密
        )

    def test_profiles_created(self):
        # 檢查 Profile 是否成功創建
        user1 = Profile.objects.get(username='user1')
        user2 = Profile.objects.get(username='user2')
        self.assertEqual(user1.email, 'user1@example.com')
        self.assertEqual(user2.email, 'user2@example.com')
    
    def test_duplicate_username(self):
        # 嘗試創建重複用戶名
        with self.assertRaises(Exception):
            Profile.objects.create(
                email='duplicate@example.com',
                username='user1',  # 重複的 username
                password=make_password('password456')
            )
    
    def test_duplicate_email(self):
        # 嘗試創建重複電子郵件
        with self.assertRaises(Exception):
            Profile.objects.create(
                email='user1@example.com',  # 重複的 email
                username='new_user',
                password=make_password('password789')
            )

    def test_password_encryption(self):
        # 確認密碼已經加密儲存
        self.assertTrue(check_password('password123', self.user1.password))
        self.assertTrue(check_password('password321', self.user2.password))

    def test_signup_api(self):
        # 測試註冊 API
        url = reverse('user_signup')  # 假設 user_signup 的 URL 名稱為 'user_signup'
        response = self.client.post(url, json.dumps({
            'username': 'user3',
            'email': 'user3@example.com',
            'password': 'password1234'
        }), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('success'))
        self.assertEqual(response.json().get('userId'), Profile.objects.get(username='user3').uid)

    def test_login_api(self):
        # 測試登入 API
        url = reverse('user_login')  # 假設 user_login 的 URL 名稱為 'user_login'
        response = self.client.post(url, json.dumps({
            'username': 'user1',
            'password': 'password123'
        }), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get('success'))

        # 錯誤密碼測試
        response = self.client.post(url, json.dumps({
            'username': 'user1',
            'password': 'wrongpassword'
        }), content_type='application/json')
        
        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.json().get('success'))
        self.assertEqual(response.json().get('err'), '密碼不正確')


