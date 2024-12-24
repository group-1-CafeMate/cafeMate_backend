from django.db import models
from django.utils import timezone
import uuid


class Cafe(models.Model):
    cafe_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True
    )
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    addr = models.CharField(max_length=100)
    work_and_study_friendly = models.BooleanField()  # true: 適合讀書或工作
    rating = models.FloatField(default=0)
    time_unlimit = models.BooleanField()
    socket = models.BooleanField(blank=True, null=True)
    pets_allowed = models.BooleanField()  # True: 寵物咖啡廳
    wiFi = models.BooleanField()
    open_hour = models.CharField(max_length=100)
    latitude = models.FloatField(null=False)
    longitude = models.FloatField(null=False)
    info = models.TextField()
    comment = models.TextField()
    ig_link = models.CharField(max_length=500, blank=True, null=True)
    gmap_link = models.CharField(max_length=500, blank=True, null=True)
    post_date = models.DateTimeField(default=timezone.now)
    ig_post_cnt = models.IntegerField()

    legal = models.BooleanField(blank=True, default=True)

    def get_labels(self):
        label_list = []
        if self.time_unlimit:
            label_list.append("不限時")
        if self.socket:
            label_list.append("插座")
        if self.pets_allowed:
            label_list.append("寵物咖啡廳")
        if self.wiFi:
            label_list.append("WiFi")
        if self.work_and_study_friendly:
            label_list.append("適合讀書或工作")
        return label_list


class OperatingHours(models.Model):
    cafe = models.ForeignKey(
        Cafe, on_delete=models.CASCADE, related_name="operating_hours"
    )
    day_of_week = models.CharField(max_length=10)
    open_time = models.CharField(max_length=25)
    close_time = models.CharField(max_length=25)

    class Meta:
        unique_together = ("cafe", "day_of_week")  # 確保每個咖啡廳的營業日唯一

    def __str__(self):
        return f"{self.cafe.name} - {self.day_of_week}: {self.open_time} to {self.close_time}"


class CafeImage(models.Model):
    cafe = models.ForeignKey(Cafe, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="cafe_images/")


class MetroStation(models.Model):
    metro_station_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    latitude = models.FloatField(null=False)
    longitude = models.FloatField(null=False)
