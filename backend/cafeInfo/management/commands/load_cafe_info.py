from django.core.management.base import BaseCommand
import json

from cafeInfo.models import Cafe


class Command(BaseCommand):
    help = "Load cafeInfo.json into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "file_path", type=str, help="The file path of the json file to load"
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs["file_path"]

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                cafes = []
                data = json.load(file)
                data = data["places"]
                for item in data:
                    cafes.append(
                        Cafe(
                            name=item["name"],
                            phone=item["phone"],
                            addr=item["address"],
                            ig_link=item["ig_location_link"],
                            gmap_link=item["gmap_link"],
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
