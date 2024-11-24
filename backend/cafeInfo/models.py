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
    quiet = models.BooleanField() # true: 適合讀書，false: 適合工作、交談
    grade = models.CharField(max_length=10)
    time_unlimit = models.BooleanField()
    time_limit = models.CharField(max_length=20) # 限時幾小時
    socket = models.BooleanField(blank = True, null = True)
    pets_allowed = models.BooleanField() # True: 寵物咖啡廳
    wiFi = models.BooleanField()
    open_hour = models.CharField(max_length=10)
    open_now = models.BooleanField()
    distance = models.FloatField()
    info = models.TextField()
    comment = models.TextField()
    ig_link = models.CharField(max_length=400, blank = True, null = True)
    fb_link = models.CharField(max_length=400, blank = True, null = True)
    post_date = models.DateTimeField(default=timezone.now)
    ig_post_cnt = models.IntegerField()

    # -------------- 以下不用顯示於前端 --------------
    legal = models.BooleanField(blank=True, null=True)

    def get_labels(self):
        label_list = []
        label_list.append("適合讀書" if self.quiet else "適合工作及交談")
        if self.time_unlimit:
            label_list.append("不限時")
        if self.socket:
            label_list.append("插座")
        if self.pets_allowed:
            label_list.append("寵物咖啡廳")
        if self.wiFi:
            label_list.append("WiFi")

        return label_list

class CafeImage(models.Model):
    cafe = models.ForeignKey(Cafe, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='cafe_images/')