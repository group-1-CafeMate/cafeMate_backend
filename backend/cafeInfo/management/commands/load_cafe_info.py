from django.core.management.base import BaseCommand
import json

from cafeInfo.models import Cafe
from django.utils import timezone


class Command(BaseCommand):
    help = "Load cafeInfo.json into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "file_path", type=str, help="The file path of the json file to load"
        )
        parser.add_argument(
            "label_file_path",
            type=str,
            help="The file path of the json file with NLP label to load",
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs["file_path"]
        label_file_path = kwargs["label_file_path"]

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                with open(label_file_path, "r", encoding="utf-8") as label_file:
                    label_data = json.load(label_file)
                    label_data = label_data["places"]
                    cafes = []
                    data = json.load(file)
                    data = data["places"]
                    for idx, item in enumerate(data):
                        if label_data[idx]["name"] != item["name"]:
                            print("incompatible item")
                            continue
                        labels = label_data[idx]["labels"]
                        cafes.append(
                            Cafe(
                                name=item["name"],
                                phone=item["phone"],
                                addr=item["address"],
                                ig_link=item["ig_link"],
                                gmap_link=item["gmap_link"],
                                rating=item["rating"],
                                ig_post_cnt=item["ig_post_cnt"],
                                latitude=item["latitude"],
                                longitude=item["longitude"],
                                info=item["info"],
                                comment=item["comment"],
                                time_unlimit=labels["unlimited_time"],
                                socket=labels["has_outlets"],
                                pets_allowed=labels["pet_friendly"],
                                wiFi=labels["has_wifi"],
                                work_and_study_friendly=labels[
                                    "work_and_study_friendly"
                                ],
                                # post_date=models.DateTimeField(default=timezone.now), #db有default value，不用設置
                            )
                        )
                    Cafe.objects.bulk_create(cafes)
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Successfully loaded {len(cafes)} metro stations."
                        )
                    )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading data: {e}"))
