from django.core.management.base import BaseCommand
import json

from cafeInfo.models import Cafe, OperatingHours
from django.utils import timezone


class Command(BaseCommand):
    help = "Load cafeInfo.json into the database. If the cafe is exist in database, the program will update it instead of create a duplicated one."

    def add_arguments(self, parser):
        parser.add_argument(
            "file_path", type=str, help="The file path of the JSON file to load"
        )
        parser.add_argument(
            "label_file_path",
            type=str,
            help="The file path of the JSON file with NLP label to load",
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs["file_path"]
        label_file_path = kwargs["label_file_path"]

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                with open(label_file_path, "r", encoding="utf-8") as label_file:
                    label_data = json.load(label_file)
                    label_data = label_data["places"]
                    data = json.load(file)
                    data = data["places"]

                    for idx, item in enumerate(data):
                        if label_data[idx]["name"] != item["name"]:
                            print("Incompatible item")
                            continue

                        # Extract labels
                        labels = label_data[idx]["labels"]

                        # Update or create Cafe object
                        cafe, created = Cafe.objects.update_or_create(
                            name=item["name"],
                            defaults={
                                "phone": item["phone"],
                                "addr": item["address"],
                                "ig_link": item["ig_link"],
                                "gmap_link": item["gmap_link"],
                                "rating": item["rating"],
                                "ig_post_cnt": item["ig_post_cnt"],
                                "latitude": item["latitude"],
                                "longitude": item["longitude"],
                                "info": item["info"],
                                "comment": item["comment"],
                                "time_unlimit": labels["unlimited_time"],
                                "socket": labels["has_outlets"],
                                "pets_allowed": labels["pet_friendly"],
                                "wiFi": labels["has_wifi"],
                                "work_and_study_friendly": labels[
                                    "work_and_study_friendly"
                                ],
                                # post_date=models.DateTimeField(default=timezone.now), #db有default value，不用設置
                            },
                        )

                        if not created:
                            print(f"Updated existing cafe: {cafe.name}")
                        else:
                            print(f"Created new cafe: {cafe.name}")

                        # Clear existing operating hours and add new ones
                        OperatingHours.objects.filter(cafe=cafe).delete()
                        business_hours = item.get("business_hours", {})
                        for day, hours in business_hours.items():
                            if hours == "休息":
                                open_time = "休息"
                                close_time = "休息"
                            else:
                                open_time, close_time = hours.split("–")

                            OperatingHours.objects.create(
                                cafe=cafe,
                                day_of_week=day,
                                open_time=open_time,
                                close_time=close_time,
                            )

                    self.stdout.write(
                        self.style.SUCCESS(f"Successfully loaded or updated data.")
                    )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading data: {e}"))
