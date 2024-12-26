import json

# 定義 20 間目標咖啡廳
target_cafes = [
    "Pica Pica Café 喜鵲咖啡",
    "Congrats Café",
    "C25度咖啡館",
    "特有種商行",
    "Orange看電車咖啡館",
    "折田菓舖",
    "勾癮咖啡GOEE COFFEE",
    "菸花Op.118.2",
    "Hater Cafe",
    "KOKU café 榖珈琲",
    "FabCafe",
    "Tiecafe",
    "遇見貓咖啡輕食館",
    "Beans & Coffee",
    "Out of office 不在辦公室",
    "湛盧咖啡（市府館）",
    "Libo cafe",
    "Miracle Coffee",
    "未央咖啡店",
    "Current Café 此刻咖啡",
]

# 讀取 places.json 檔案
with open("places.json", "r", encoding="utf-8") as file:
    places_data = json.load(file)

# 過濾出目標咖啡廳
filtered_places_info = []
filtered_places_intro_and_reviews = []

for place in places_data["places"]:
    if place["name"] in target_cafes:
        # 基本資訊（去掉 google_reviews）
        place_info = {k: v for k, v in place.items() if k != "google_reviews"}
        filtered_places_info.append(place_info)

        # 店名與 google_reviews
        intro_and_reviews = {
            "name": place["name"],
            "google_reviews": place.get("google_reviews", []),
        }
        filtered_places_intro_and_reviews.append(intro_and_reviews)

# 將基本資訊寫入 top_20_places_info.json
with open("top20_cafes_info.json", "w", encoding="utf-8") as info_file:
    json.dump({"places": filtered_places_info}, info_file, ensure_ascii=False, indent=4)

# 將店名與 google_reviews 寫入 top_20_places_intro_and_reviews.json
with open(
    "top20_cafes_intro_and_reviews.json", "w", encoding="utf-8"
) as intro_reviews_file:
    json.dump(
        filtered_places_intro_and_reviews,
        intro_reviews_file,
        ensure_ascii=False,
        indent=4,
    )

print("過濾完成，資料已分別儲存到 top20_cafes_info.json 和 top20_cafes_intro_and_reviews.json")
