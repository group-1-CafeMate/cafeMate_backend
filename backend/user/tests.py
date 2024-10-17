from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from .models import Profile
from django.contrib.auth.hashers import make_password

class ProfileTestCase(TestCase):
    def setUp(self):
        # 創建測試用的 Profile 實例
        Profile.objects.create(
            email='user1@example.com',
            username='user1',
            password=make_password('password123'),  # 實際應用中應該使用加密過的密碼
        )
        Profile.objects.create(
            email='user2@example.com',
            username='user2',
            password=make_password('password321'),  # 實際應用中應該使用加密過的密碼
        )

    def test_profiles_created(self):
        # 檢查創建的 Profile 是否存在
        user1 = Profile.objects.get(username='user1')
        user2 = Profile.objects.get(username='user2')
        self.assertEqual(user1.email, 'user1@example.com')
        self.assertEqual(user2.email, 'user2@example.com')

