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