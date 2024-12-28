import math
from typing import List, Tuple
from .models import Cafe

from django.contrib.sites.shortcuts import get_current_site


def generate_image_url(request, relative_path: str) -> str:
    site_url = f"http://{get_current_site(request).domain}/"
    return f"{site_url}{relative_path}"


class LatitudeLongitude:
    def __init__(self, latitude: float, longitude: float):
        self.latitude = latitude
        self.longitude = longitude
        self.validate()

    def validate(self):
        if not (-90 <= self.latitude <= 90):
            raise ValueError("緯度必須在 -90 到 90 之間")
        if not (-180 <= self.longitude <= 180):
            raise ValueError("經度必須在 -180 到 180 之間")

    def distance_to(self, other: "LatitudeLongitude") -> float:
        """
        計算與另一個經緯度點的距離 (公里)。
        使用 Haversine formula。
        """
        if not isinstance(other, LatitudeLongitude):
            raise TypeError("參數必須是 LatitudeLongitude 類別的實例")

        # 地球半徑（公里）
        R = 6371.0

        # 將經緯度從度數轉換為弧度
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other.latitude), math.radians(other.longitude)

        # 哈弗賴公式計算
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c

        return distance


def calculate_and_sort_cafes(
    cafes: List[Cafe], user_location: LatitudeLongitude | None
) -> List[Tuple[float, Cafe]]:
    """
    計算每個 Cafe 與用戶的距離並依距離排序。

    :param cafes: Cafe 的列表。
    :param user_lat: 用戶當前的緯度。
    :param user_lon: 用戶當前的經度。
    :return: 包含距離和 Cafe 的列表，依距離排序。
    """
    if user_location is None:
        return [(-1, c) for c in cafes]
    try:
        # 計算每個 Cafe 的距離
        cafes_with_distances = []
        for cafe in cafes:
            if cafe.latitude is None or cafe.longitude is None:
                continue  # 跳過沒有經緯度的 Cafe

            try:
                cafe_location = LatitudeLongitude(cafe.latitude, cafe.longitude)
                distance = user_location.distance_to(cafe_location)
                cafes_with_distances.append((distance, cafe))
            except ValueError:
                continue  # 若經緯度格式有誤，跳過

        # 根據距離進行排序
        cafes_with_distances.sort(key=lambda x: x[0])

        return cafes_with_distances
    except Exception as e:
        raise ValueError(f"Error in calculating and sorting cafes: {str(e)}")
