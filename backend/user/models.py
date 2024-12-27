from django.db import models
from django.utils import timezone

# from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
import uuid


# Create your models here.
class Profile(models.Model):
    # user = models.OneToOneField(User, on_delete=models.CASCADE, null = False, blank = True)
    uid = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    email = models.EmailField(max_length=50, null=False, blank=True)
    username = models.CharField(max_length=20, null=False, blank=True)
    password = models.CharField(max_length=220, null=False, blank=True)
    date = models.DateTimeField(default=timezone.now)

    def authenticate(self, password):
        return check_password(password, self.password)
