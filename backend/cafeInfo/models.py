from django.db import models
from user.models import Profile
from django.utils import timezone
import uuid
# Create your models here.

class Cafe(models.Model):
    cafe_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    addr = models.CharField(max_length=100)
    quiet = models.BooleanField()
    grade = models.CharField(max_length=10)
    time_limit = models.CharField(max_length=50)
    socket = models.BooleanField(blank = True, null = True)
    pets_allowed = models.BooleanField()
    wiFi = models.BooleanField()
    open_hour = models.CharField(max_length=10)
    open_now = models.BooleanField()
    distance = models.FloatField()
    info = models.TextField()
    comment = models.TextField()
    ig_hashtag_cnt = models.IntegerField()
    google_review_cnt = models.IntegerField()
    google_review_link = models.CharField(max_length=500, blank = True, null = True)
    ig_link = models.CharField(max_length=500, blank = True, null = True)
    fb_link = models.CharField(max_length=500, blank = True, null = True)
    post_date = models.DateTimeField(default=timezone.now)
    legal = models.BooleanField(blank=True, null=True)
    # owner = models.ForeignKey(Profile, on_delete=models.CASCADE)


class CafeImage(models.Model):
    cafe = models.ForeignKey(Cafe, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='cafe_images/')