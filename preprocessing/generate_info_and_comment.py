"""
Used to generate a unique profile of each cafe and comprehensive customer reviews
"""
import json
import tiktoken
import openai
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
import os
import logging

# 初始化日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 載入 .env 檔案
load_dotenv(Path(__file__).resolve().parent / "../backend/backend/.env")

# 從環境變數讀取 API key
key = os.getenv("OPENAI_API_KEY")
if not key:
    raise EnvironmentError("OPENAI_API_KEY not found in .env file")

client = OpenAI(api_key=key)

# 初始化 tiktoken 編碼器
encoder = tiktoken.encoding_for_model("gpt-4o-mini")

# 計算 token 數量
def calculate_tokens(text):
    return len(encoder.encode(text))

# 初始化總 token 計數
total_tokens = 0
output_tokens = 0

# 定義處理文字的函數
def process_text(messages, max_input_tokens=400, max_output_tokens=300):
    global total_tokens, output_tokens
    try:
        # 計算輸入 token 數量
        input_tokens = sum(calculate_tokens(message["content"]) for message in messages)
        total_tokens += input_tokens

        # 如果輸入 token 數量超過 max_input_tokens，則截斷消息內容
        if input_tokens > max_input_tokens:
            truncated_messages = []
            current_tokens = 0

            for message in messages:
                content_tokens = calculate_tokens(message["content"])
                if current_tokens + content_tokens > max_input_tokens:
                    # 截斷消息內容
                    available_tokens = max_input_tokens - current_tokens
                    truncated_content = encoder.decode(encoder.encode(message["content"])[:available_tokens])
                    truncated_messages.append({"role": message["role"], "content": truncated_content})
                    break
                else:
                    truncated_messages.append(message)
                    current_tokens += content_tokens

            messages = truncated_messages

        # 發送請求給 OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=max_output_tokens,
            temperature=1.0
        )

        # 計算輸出的 token 數量
        response_content = response.choices[0].message.content.strip()
        response_tokens = calculate_tokens(response_content)

        output_tokens += response_tokens

        return response_content

    except Exception as e:
        logger.error(f"Error processing GPT request: {e}")
        return None

# 讀取 JSON 文件
try:
    with open("top20_cafes.json", "r", encoding="utf-8") as file:
        data = json.load(file)
except FileNotFoundError:
    raise FileNotFoundError("top20_cafes.json file not found.")
except json.JSONDecodeError:
    raise ValueError("Error decoding JSON from top20_cafes.json")

# 生成每間咖啡廳的專屬介紹及顧客綜合評論
results = []

for place in data["places"]:
    cafe_name = place.get("name", "Unknown Cafe")
    ig_contents = []
    google_reviews = []
    
    # 收集 IG 貼文內容
    for ig_review in place.get("ig_contents", []):
        ig_contents.extend(ig_review.get("content", []))
    
    # 收集 Google 評論
    for google_review in place.get("google_reviews", []):
        google_reviews.append(google_review.get("review_text", ""))
    
    # f-string 裡面不能有 '\'字樣，因此設成變數餵進去
    line_break = '\n' 

    # 如果內容為空，跳過 GPT 請求
    if not ig_contents:
        cafe_description = "No IG content available for this cafe."
    else:
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
            若有限時間的話請幫我特別註明限時幾小時。
        """}
        ]
        cafe_description = process_text(ig_messages, max_input_tokens=10000, max_output_tokens=800)

    if not google_reviews:
        customer_feedback = "No Google reviews available for this cafe."
    else:    
        # 將 Google 評論丟進 GPT，生成顧客綜合評論
        google_messages = [
            {"role": "system", "content": "你是一個專業的顧客評論分析助手。"},
            {"role": "user", "content": f"""以下是關於咖啡廳 {cafe_name} 的 Google 評論：{line_break}
                {line_break.join(google_reviews)}{line_break}
                請基於這些內容，撰寫該咖啡廳的顧客綜合評論，可以對食物跟環境(店內風格)有多一點評論，並且希望人性化一點。"""}
        ]
        customer_feedback = process_text(google_messages, max_input_tokens=10000, max_output_tokens=300)

    # 將生成的內容寫回 JSON object
    place["info"] = cafe_description
    place["comment"] = customer_feedback

# 將結果輸出到 JSON 文件
with open("top20_cafes.json", "w", encoding="utf-8") as output_file:
    json.dump(data, output_file, ensure_ascii=False, indent=4)

print("生成完成！結果已儲存在 top20_cafes.json 文件中。")

# 輸出總 token 數量
print(f"總輸入 token 數量：{total_tokens}")
print(f"總輸出 token 數量：{output_tokens}")