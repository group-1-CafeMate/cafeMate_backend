from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from user.models import Profile
import uuid

# Create your models here.
class Administrator(models.Model):
    admin_uid = models.UUIDField(primary_key= True,default=uuid.uuid4, editable=False, unique=True)
    user_id = models.ForeignKey(Profile, on_delete=models.CASCADE, db_column='uid')
    admin_name = models.CharField(max_length = 20, null = False, blank = True)
    password = models.CharField(max_length = 128, null = False, blank = True)
    email = models.EmailField(max_length = 50, null = False, blank = True)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        print(self.password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
    
    def __str__(self):
        return self.admin_name

class Cafe(models.Model):
    cafe_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    cafe_name = models.CharField(max_length=100, null=False, blank=False)
    location = models.CharField(max_length=200, null=True, blank=True)
    legal = models.BooleanField(null=True)  # 用於表示咖啡廳是否通過合法性審核
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='cafes')  # 關聯到 Profile，表示擁有者

    def __str__(self):
        return self.cafe_name