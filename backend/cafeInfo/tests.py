from django.test import TestCase, Client
from django.urls import reverse
from .models import Cafe, CafeImage, MetroStation
import uuid


class CafeViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Create a test MetroStation
        self.metro_station = MetroStation.objects.create(
            name="Test Station", latitude=25.033, longitude=121.565
        )

        # Create a test Cafe
        self.cafe = Cafe.objects.create(
            cafe_id=uuid.uuid4(),
            name="Test Cafe",
            phone="123-456-7890",
            addr="123 Test St",
            work_and_study_friendly=True,
            rating=4.5,
            time_unlimit=True,
            socket=True,
            pets_allowed=False,
            wiFi=True,
            latitude=25.034,
            longitude=121.564,
            info="A great place to work.",
            comment="Spacious and clean.",
            ig_link="https://instagram.com/testcafe",
            gmap_link="https://googlemap.com/testcafe",
            ig_post_cnt=100,
            legal=True,
        )

        # Add an image to the Cafe
        CafeImage.objects.create(cafe=self.cafe, image="test_image.jpg")

    def test_get_all_cafes(self):
        response = self.client.get(
            reverse("get_all_cafes"), {"latitude": 25.033, "longitude": 121.565}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("cafes", response.json())
        self.assertTrue(response.json()["success"])

    def test_get_cafe(self):
        response = self.client.get(
            reverse("get_cafe"), {"cafe_id": str(self.cafe.cafe_id)}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("cafe", response.json())
        self.assertTrue(response.json()["success"])

    def test_filter_cafes_by_labels(self):
        response = self.client.get(
            reverse("filter_cafes_by_labels"),
            {"time_unlimit": True, "latitude": 25.033, "longitude": 121.565},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("cafes", response.json())
        self.assertTrue(response.json()["success"])

    def test_get_all_cafes_with_invalid_location(self):
        response = self.client.get(
            reverse("get_all_cafes"), {"latitude": "invalid", "longitude": "invalid"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("message", response.json())
        self.assertFalse(response.json()["success"])
