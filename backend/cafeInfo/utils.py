import math


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


def sort_cafes_by_distance(cafes):
    cafe_info_with_distance = []
    for cafe in cafes:
        try:
            cafe_location = LatitudeLongitude(cafe.latitude, cafe.longitude)
            distance = user_location.distance_to(cafe_location)
        except ValueError:
            continue  # 如果經緯度有問題，跳過該咖啡廳

        cafe_info_with_distance.append(
            {
                "cafe_id": str(cafe.cafe_id),
                "name": cafe.name,
                "grade": cafe.grade,
                "open_hour": cafe.open_hour,
                "open_now": cafe.open_now,
                "distance": round(distance, 4),
                "labels": cafe.get_labels(),
                "image_url": (
                    cafe.images.all()[0].image.url if cafe.images.exists() else None
                ),
            }
        )

    # 根據距離排序
    cafe_info_with_distance.sort(key=lambda x: x["distance"])
    return cafe_info_with_distance
