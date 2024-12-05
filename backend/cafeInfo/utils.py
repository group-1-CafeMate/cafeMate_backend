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
