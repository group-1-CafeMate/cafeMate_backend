import json
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence
 
# 定義關鍵詞
keywords = {
    "unlimited_time": ["不限時", "無時間限制", "無限制時間", "長時間坐", "長時間停留", "無限時", "久坐"],
    "has_outlets": ["提供插座", "插座", "充電", "充電設施", "電源供應", "充電插座"],
    "pet_friendly": ["寵物友善", "寵物入內", "可帶寵物", "歡迎寵物", "寵物允許", "寵物隨行", "貓友善", 
                     "狗友善", "貓", "狗", "貓咪", "撸貓", "店貓"],
    "has_wifi": ["WiFi", "提供 WiFi", "免費 WiFi", "無線網路", "無線上網", "WiFi 服務", "網路連接"],
    "work_and_study_friendly": ["安靜", "寧靜", "不吵", "低噪音", "適合讀書", "適合交談", "適合聊天", "輕鬆交談", "適合談事情"],
}

# 訓練 Word2Vec 模型
print("訓練 Word2Vec 模型中...")
sentences = LineSentence("tokenized_reviews.txt")  # 使用分詞後的評論文件
model = Word2Vec(sentences, vector_size=100, window=4, min_count=1, workers=4)

# 生成每個類別的擴展關鍵詞，並篩選前10名
expanded_keywords = {}
for category, words in keywords.items():
    related_words = []
    for word in words:
        if word in model.wv:
            related_words += model.wv.most_similar(word, topn=10)  # 取得每個關鍵詞的前10個相關詞

    # 合併原始關鍵詞及相關詞，並按相似度排序後取前10名
    unique_related_words = {word: similarity for word, similarity in related_words}  # 去重
    for word in words:
        unique_related_words[word] = 1.0  # 確保原始關鍵詞相似度為 1.0

    # 排序並取前10名
    sorted_words = sorted(unique_related_words.items(), key=lambda x: x[1], reverse=True)[:10]
    expanded_keywords[category] = [word for word, _ in sorted_words]

# 將擴展關鍵詞輸出到 JSON 檔案
with open("expanded_keywords.json", "w", encoding="utf-8") as file:
    json.dump(expanded_keywords, file, ensure_ascii=False, indent=4)

print("擴展關鍵詞已儲存到 expanded_keywords.json")
