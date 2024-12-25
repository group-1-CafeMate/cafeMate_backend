import json

# 讀取 places.json 檔案
with open("top20_cafes.json", "r", encoding="utf-8") as file:
    places_data = json.load(file)

cafes_info = []
cafes_contents_and_reviews = []

for place in places_data["places"]:
    # 基本資訊（去掉 google_reviews）
    place_info = {k: v for k, v in place.items() if k != "google_reviews"}
    cafes_info.append(place_info)

    # 店名與 google_reviews
    contents_and_reviews = {
        "name": place["name"],
        "google_reviews": place.get("google_reviews", [])
    } 
    cafes_contents_and_reviews.append(contents_and_reviews)

# 將基本資訊寫入 top_20_places_info.json
with open("top20_cafes_info.json", "w", encoding="utf-8") as info_file:
    json.dump({"places": cafes_info}, info_file, ensure_ascii=False, indent=4)

# 將店名與 google_reviews 寫入 top20_cafes_contents_and_reviews.json
with open("top20_cafes_contents_and_reviews.json", "w", encoding="utf-8") as contents_reviews_file:
    json.dump({"places": cafes_contents_and_reviews}, contents_reviews_file, ensure_ascii=False, indent=4)


print("過濾完成，資料已分別儲存到 top20_cafes_info.json 和 top20_cafes_contents_and_reviews.json")
