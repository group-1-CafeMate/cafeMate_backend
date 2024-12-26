import json
import jieba
 
# 讀取擴展關鍵詞
with open("expanded_keywords.json", "r", encoding="utf-8") as file:
    expanded_keywords = json.load(file)
 
# 分詞處理
def tokenize_reviews(reviews):
    tokenized_reviews = []
    for review in reviews:
        text = review.get("review_text", "")
        tokens = list(jieba.cut(text))
        tokenized_reviews.append(tokens)
    return tokenized_reviews

# 匹配評論中的關鍵詞
def match_keywords_in_reviews(reviews, keywords):
    tokenized_reviews = tokenize_reviews(reviews)

    # 初始化每個標籤為 False
    result = {category: False for category in keywords.keys()}

    # 遍歷每個分類的關鍵詞
    for category, words in keywords.items():
        for tokens in tokenized_reviews:
            if any(token in words for token in tokens):
                result[category] = True
                break  # 找到相關詞後，標記為 True 並跳出該分類檢查

    return result

# 讀取 top20_cafe_info.json
with open("../top20_cafes_info.json", "r", encoding="utf-8") as file:
    cafe_data = json.load(file)

# 讀取 top20_cafes_contents_and_reviews.json
with open("../top20_cafes_contents_and_reviews.json", "r", encoding="utf-8") as file:
    review_data = json.load(file)

# 更新每間咖啡廳的標籤
for cafe_info in cafe_data["places"]:
    # 在 review_data 中找到對應的咖啡廳
    matching_cafe = next((cafe for cafe in review_data["places"] if cafe["name"] == cafe_info["name"]), None)

    if matching_cafe:
        reviews = matching_cafe.get("google_reviews", [])
        matched_labels = match_keywords_in_reviews(reviews, expanded_keywords)
        
        # 更新或新增 labels
        cafe_info["labels"] = matched_labels

# 將更新後的資料寫回 top20_cafe_info.json
with open("../top20_cafes_info.json", "w", encoding="utf-8") as file:
    json.dump(cafe_data, file, ensure_ascii=False, indent=4)

print("標籤已成功寫入 top20_cafes_info.json")
