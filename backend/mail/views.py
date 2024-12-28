from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
import json
from user.models import Profile
from .tasks import email_token, send_custom_email
import string
import random
from django.core.mail import send_mail


# 註冊後，寄送驗證信至使用者信箱
@csrf_exempt
def send_email_view(request):
    if request.method == "POST" and request.content_type == "application/json":
        try:
            data = json.loads(request.body)
            email = data.get("email")
            name = data.get("name")
            token = email_token()
            token_s = token.generate_token(email)
            print("Email:", email)
            print("Name:", name)
            send_custom_email(email, name, token_s)  # Call the task to send the email
            message = {"status": "0", "token": token_s}
        except Exception as e:
            print(e)
            message = {"status": "1", "message": "Error sending email"}

        return JsonResponse(message)
    else:
        return JsonResponse(
            {"status": "1", "message": "Invalid request method or content type"}
        )


# 寄送隨機產生的新密碼至忘記密碼的使用者信箱
@csrf_exempt
def forgot(request):  # 忘記密碼
    if request.method == "POST" and request.content_type == "application/json":
        try:
            # 解析請求的 JSON 資料
            data = json.loads(request.body)
            email = data.get("email")
            if not email:
                return JsonResponse(
                    {"status": "1", "message": "Email is required"}, status=400
                )

            # 查找用戶
            user = Profile.objects.get(email=email)

            # 生成新的密碼
            chars = string.ascii_letters + string.digits
            new_pw = "".join(random.sample(chars, 16))
            hashed_pw = make_password(new_pw)

            # 更新用戶密碼
            rows_updated = Profile.objects.filter(email=email).update(
                password=hashed_pw
            )
            if rows_updated == 0:
                raise Exception("Password update failed: No matching user found")

            # 準備郵件內容
            title = "找回密碼"
            sender = settings.EMAIL_HOST_USER
            msg = "\n".join([f"歡迎 {user.username}", f"新的密碼為:\n{new_pw}"])

            # 寄送郵件
            send_mail(title, msg, sender, [email])

            # 返回成功訊息
            return JsonResponse({"status": "0", "message": "Password reset email sent"})
        except Profile.DoesNotExist:
            # 用戶不存在
            return JsonResponse(
                {"status": "1", "message": "User not found"}, status=404
            )
        except Exception as e:
            # 處理其他例外情況
            print("Error:", e)
            return JsonResponse(
                {"status": "1", "message": "Error sending email"}, status=500
            )

    # 如果不是 POST 請求，返回錯誤
    return JsonResponse(
        {"status": "1", "message": "Invalid request method"}, status=405
    )
