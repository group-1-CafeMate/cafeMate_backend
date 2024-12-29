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
            username = data.get("username")
            if not username:
                return JsonResponse(
                    {"status": "1", "message": "User is required"}, status=400
                )

            # 查找用戶
            user = Profile.objects.get(username=username)
            # 用戶電子信箱
            email = user.email

            # 生成新的密碼
            chars = string.ascii_letters + string.digits
            new_pw = "".join(random.sample(chars, 16))
            hashed_pw = make_password(new_pw)

            # 更新用戶密碼
            rows_updated = Profile.objects.filter(username=username).update(
                password=hashed_pw
            )
            if rows_updated == 0:
                raise Exception("Password update failed: No matching user found")

            # 準備郵件內容 (HTML格式)
            title = "CafeMate 密碼重設"
            sender = settings.EMAIL_HOST_USER
            msg = f"""
            <html>
                <body>
                    <h2>親愛的 {user.username}，</h2>
                    <p>感謝您使用 CafeMate！您的新密碼已經重設成功。以下是您的新密碼：</p>
                    <p><strong>新密碼：</strong>{new_pw}</p>
                    <p>為了保護您的帳戶安全，建議您在首次登入後立即修改密碼。</p>
                    <p>如果您未進行此操作，請忽略此郵件。</p>
                    <br>
                    <p>祝您使用愉快！</p>
                    <p>— CafeMate 團隊</p>
                </body>
            </html>
            """

            # 寄送郵件，設置 HTML 格式
            send_mail(
                title,  # 郵件標題
                "",  # 這裡的內容是空的，因為我們將 HTML 內容設置在 html_message 中
                sender,  # 發件人
                [email],  # 收件人
                html_message=msg,  # 這是 HTML 格式的內容
            )

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
