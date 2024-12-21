import json
import jieba
import time
from sentence_transformers import SentenceTransformer, util

# 定義關鍵詞
keywords = {
    "unlimited_time": ["不限時", "無時間限制", "無限制時間", "長時間坐", "長時間停留", "無限時", "久坐"],

    "has_outlets": ["提供插座", "插座", "充電", "充電設施", "電源供應", "充電插座"],

    "pet_friendly": ["寵物友善", "寵物入內", "可帶寵物", "歡迎寵物", "寵物允許", "寵物隨行", 
                     "狗友善", "貓", "狗", "貓咪", "撸貓", "店貓"],

    "has_wifi": ["WiFi", "提供WiFi", "免費WiFi", "無線網路", "無線上網", "WiFi服務", "網路連接", "wifi", "提供wifi"],

    "quiet_study": ["安靜", "寧靜", "不吵", "低噪音", "適合讀書", "沒有吵雜聲", "專注環境", "無干擾"],

    "suitable_for_meeting": ["適合交談", "適合聊天", "輕鬆交談", "適合討論", "適合工作", 
                             "聚會場所", "方便開會", "適合談事情"]
}

start_time = time.time()

# 初始化 BERT 模型
print("Loading BERT model...")
bert_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
# bert_model = SentenceTransformer("uer/sbert-base-chinese-nli")

# 查找與關鍵詞相似的詞彙
def find_similar_words_bert(keywords, model, topn=10):
    similar_words = {}
    for category, words in keywords.items():
        category_similar_words = []
        for word in words:
            query_embedding = model.encode(word)

            # 使用詞庫中的詞計算相似性
            all_words = list(set(sum(keywords.values(), [])))  # 展平成所有關鍵詞的集合
            corpus_embeddings = model.encode(all_words)
            similarity_scores = util.pytorch_cos_sim(query_embedding, corpus_embeddings)[0]

            # 取得最相似的詞
            top_results = similarity_scores.argsort(descending=True)[:topn]
            for idx in top_results:
                category_similar_words.append((all_words[idx], similarity_scores[idx].item()))

        # 去重並排序
        unique_similar_words = {word: score for word, score in category_similar_words}
        sorted_similar_words = sorted(unique_similar_words.items(), key=lambda x: x[1], reverse=True)[:topn]
        similar_words[category] = sorted_similar_words

    return similar_words

# 為每個關鍵詞分類匹配相關詞
print("Finding similar words...")
all_similar_words = find_similar_words_bert(keywords, bert_model, topn=10)

# 打印結果
for category, similar_words in all_similar_words.items():
    print(f"\nCategory: {category}")
    for sim_word, similarity in similar_words:
        print(f"  {sim_word} (similarity: {similarity:.4f})")

end_time = time.time()
 
elapsed_time = end_time - start_time
minutes = int(elapsed_time // 60)
seconds = int(elapsed_time % 60)
print(f"\n程式執行時間：{minutes} 分 {seconds} 秒")
