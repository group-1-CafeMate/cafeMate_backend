import csv
from django.core.management.base import BaseCommand

from cafeInfo.models import MetroStation


class Command(BaseCommand):
    help = "Load metro station data from a CSV file into the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "file_path", type=str, help="The file path of the CSV file to load"
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs["file_path"]

        try:
            with open(file_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                stations = [
                    MetroStation(
                        name=row["station_name_tw"],
                        latitude=float(row["lat"]),
                        longitude=float(row["lon"]),
                    )
                    for row in reader
                ]
                MetroStation.objects.bulk_create(stations)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully loaded {len(stations)} metro stations."
                    )
                )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error loading data: {e}"))
