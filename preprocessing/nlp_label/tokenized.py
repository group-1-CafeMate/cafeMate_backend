import json
import jieba
import time

# 加載停用詞表
def load_stopwords(file_path="stopwords.txt"):
    with open(file_path, "r", encoding="utf-8") as f:
        stopwords = set(f.read().splitlines())
    return stopwords

stopwords = load_stopwords()

# 定義關鍵詞分類
keywords = {
    "unlimited_time": ["不限時", "無時間限制", "長時間坐", "長時間停留", "無限時", "久坐"],
    "has_outlets": ["提供插座", "插座", "充電", "充電設施", "電源供應", "充電插座"],
    "pet_friendly": ["寵物友善", "寵物入內", "可帶寵物", "歡迎寵物", "寵物允許", "寵物隨行", "貓友善", "狗友善"],
    "has_wifi": ["WiFi", "提供WiFi", "免費WiFi", "無線網路", "無線上網", "WiFi服務", "網路連接"],
    "quiet_study": ["安靜", "寧靜", "不吵", "低噪音", "適合讀書", "沒有吵雜聲", "專注環境", "無干擾"],
    "suitable_for_meeting": ["適合交談", "適合聊天", "輕鬆交談", "適合討論", "適合工作", "聚會場所", "方便開會", "適合談事情"]
}

# 將關鍵詞加入 jieba 詞典
def add_keywords_to_jieba(keywords):
    for category, words in keywords.items():
        for word in words:
            jieba.add_word(word)  # 添加關鍵詞到 jieba 詞典

# 添加關鍵詞到 jieba
add_keywords_to_jieba(keywords)

# 分詞並保存到文本文件
def save_tokenized_reviews_to_file(reviews, output_file="tokenized_reviews.txt"):
    with open(output_file, "w", encoding="utf-8") as f:
        for review in reviews:
            text = review.get("review_text", "")
            # 分詞並過濾停用詞
            tokens = [word for word in jieba.cut(text) if word not in stopwords and len(word.strip()) > 1]
            f.write(" ".join(tokens) + "\n")  # 每條評論寫成一行

# 讀取 JSON 文件並保存分詞結果到文本
with open("places.json", "r", encoding="utf-8") as file:
    data = json.load(file)

all_reviews = []
for place in data.get("places", []):
    reviews = place.get("reviews", [])
    all_reviews.extend(reviews)
 
# 保存分詞後的文本
save_tokenized_reviews_to_file(all_reviews)