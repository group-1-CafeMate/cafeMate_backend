"""
Used to generate a unique profile of each cafe and comprehensive customer reviews
"""
import json
import tiktoken
import openai
from openai import OpenAI
from dotenv import load_dotenv
import os

# 載入 .env 檔案
load_dotenv("../backend/backend/.env")

# 從環境變數讀取 API key
key = os.getenv("OPENAI_API_KEY")

client = OpenAI(
    api_key= key 
)

# 初始化 tiktoken 編碼器
encoder = tiktoken.encoding_for_model("gpt-4o-mini")
 
# 計算 token 數量
def calculate_tokens(text):
    return len(encoder.encode(text))

# 初始化總 token 計數
total_tokens = 0
output_tokens = 0  # 用來儲存輸出的 token 總數

# 定義處理文字的函數
def process_text(messages, max_tokens=400):
    global total_tokens, output_tokens
    try:
        # 計算輸入 token 數量
        input_tokens = sum(calculate_tokens(message["content"]) for message in messages)
        total_tokens += input_tokens
        
        # 檢查 token 是否超出限制
        if input_tokens > max_tokens:
            raise ValueError(f"輸入的 token 數量已超出限制！目前: {input_tokens}, 最大: {max_tokens}")
        
        # 發送請求給 OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=max_tokens,  # 留出輸出 token 空間
            temperature=1.0
        )
        
        # 計算輸出的 token 數量
        response_content = response.choices[0].message.content.strip()
        response_tokens = calculate_tokens(response_content)
        output_tokens += response_tokens

        return response_content
    except Exception as e:
        print(f"Error processing GPT request: {e}")
        return None

# 讀取 places.json 文件
with open("Pica_Cafe_igposts_google.json", "r", encoding="utf-8") as file:
    data = json.load(file)

# 生成每間咖啡廳的專屬介紹及顧客綜合評論
results = []

for place in data["places"]:
    cafe_name = place.get("name", "Unknown Cafe")
    ig_contents = []
    google_reviews = []
    
    # 收集 IG 貼文內容
    for ig_review in place.get("ig_reviews", []):
        ig_contents.extend(ig_review.get("content", []))
    
    # 收集 Google 評論
    for google_review in place.get("google_reviews", []):
        google_reviews.append(google_review.get("review_text", ""))
    
    # f-string 裡面不能有 '\'字樣，因此設成變數餵進去
    line_break = '\n' 

    # 將 IG 貼文丟進 GPT，生成專屬介紹
    ig_messages = [
    {"role": "system", "content": "你是一個專業的文案撰寫助手。"},
    {"role": "user", "content": f"""
        以下是關於咖啡廳 {cafe_name} 的 IG 貼文內容：
        {line_break.join(ig_contents)}
        請基於這些內容，撰寫該咖啡廳的專屬介紹。
        可以提到：
        - 環境、氣氛
        - 咖啡與餐點（價格、種類、好吃程度）
        - 讀書工作：Wi-Fi、安靜程度、插座
        - 聚會聊天：空間、氣氛、餐點多樣性
        - 放鬆獨處：景觀、音樂、座位舒適性。
    """}
    ]
    cafe_description = process_text(ig_messages, max_tokens=5000)

    # 將 Google 評論丟進 GPT，生成顧客綜合評論
    google_messages = [
        {"role": "system", "content": "你是一個專業的顧客評論分析助手。"},
        {"role": "user", "content": f"""以下是關於咖啡廳 {cafe_name} 的 Google 評論：{line_break}
            {line_break.join(google_reviews)}{line_break}
            請基於這些內容，撰寫該咖啡廳的顧客綜合評論，可以對食物跟環境(店內風格)有多一點評論。"""}
    ]
    customer_feedback = process_text(google_messages, max_tokens=4000)

    # 儲存結果
    results.append({
        "name": cafe_name,
        "description": cafe_description,
        "customer_feedback": customer_feedback
    })

# 將結果輸出到 JSON 文件
with open("cafe_results.json", "w", encoding="utf-8") as output_file:
    json.dump(results, output_file, ensure_ascii=False, indent=4)

print("生成完成！結果已儲存在 cafe_results.json 文件中。")

# 輸出總 token 數量
print(f"總輸入 token 數量：{total_tokens}")
print(f"總輸出 token 數量：{output_tokens}")