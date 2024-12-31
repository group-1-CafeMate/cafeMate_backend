from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.views.decorators.csrf import csrf_exempt
import json
from user.models import Profile
from .tasks import email_token, enqueue_email
import string
import random
import logging

logger = logging.getLogger(__name__)


# 註冊後，將郵件發送請求排入隊列
@csrf_exempt
def enqueue_verification_email(request):
    if request.method == "POST" and request.content_type == "application/json":
        try:
            data = json.loads(request.body)
            email = data.get("email")
            name = data.get("name")
            EmailTokenManager = email_token()
            token_s = EmailTokenManager.generate_token(email)
            print("Email:", email)
            print("Nameeee:", name)
            enqueue_email.delay(
                email,
                name,
                token_s,
                "verification",  # 信件類別為驗證信
            )  # 使用 Celery 任務
            message = {
                "status": "success",
                "token": token_s,
            }
        except Exception as e:
            print(e)
            message = {
                "status": "error",
                "message": "Error sending email",
            }

        return JsonResponse(message)
    else:
        return JsonResponse(
            {
                "status": "error",
                "message": "Invalid request method or content type",
            }
        )


@csrf_exempt
def enqueue_forgot_email(request):  # 忘記密碼
    if request.method == "POST" and request.content_type == "application/json":
        try:
            # 解析請求的 JSON 資料
            data = json.loads(request.body)
            username = data.get("username")
            if not username:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "Username is required",
                    },
                    status=400,
                )

            # 查找用戶
            user = Profile.objects.get(username=username)

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

            # 準備發送郵件的參數
            email = user.email
            name = user.username
            # 使用 Celery 發送郵件
            enqueue_email.delay(
                email,
                name,
                new_pw,
                "forgot_password",  # 信件類別為密碼重設信
            )

            # 返回成功訊息
            return JsonResponse(
                {
                    "status": "success",
                    "message": "Password reset email queued for sending",
                }
            )
        except Profile.DoesNotExist:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "User not found",
                },
                status=404,
            )
        except Exception as e:
            print("Error:", e)
            return JsonResponse(
                {
                    "status": "error",
                    "message": "Internal server error",
                },
                status=500,
            )

    # 如果不是 POST 請求，返回錯誤
    return JsonResponse(
        {
            "status": "error",
            "message": "Invalid request method",
        },
        status=405,
    )
