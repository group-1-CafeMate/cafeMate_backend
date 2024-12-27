from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

# from django.contrib.auth.models import User
from user.decorators import login_required

from .models import Profile
import json
from mail.tasks import email_token


# Create your views here.
@csrf_exempt
def sign_up(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    try:
        if request.content_type == "application/json":
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse(
                    {"status": 400, "message": "請求不是有效的 JSON"}, status=400
                )
            email = data.get("email")
            username = data.get("username")
            password = data.get("password")
        else:
            email = request.POST.get("email")
            username = request.POST.get("username")
            password = request.POST.get("password")

        if not email or not username or not password:
            return JsonResponse({"status": 400, "message": "缺少必要字段"}, status=400)

        try:
            validate_password(password)
        except ValidationError as e:
            return JsonResponse({"status": 400, "message": e.messages}, status=400)

        encrypted_password = make_password(password)
        print(f"加密後的密碼: {encrypted_password}")
        print(f"長度: {len(encrypted_password)}")

        # 檢查用戶名和電子郵件是否重複
        if Profile.objects.filter(email=email).exists():
            return JsonResponse(
                {"status": 400, "message": "電子郵件已存在"}, status=400
            )
        if Profile.objects.filter(username=username).exists():
            return JsonResponse({"status": 400, "message": "用戶名已存在"}, status=400)

        # 創建新用戶
        profile = Profile.objects.create(
            email=email, username=username, password=encrypted_password
        )
        profile.save()

        # 返回成功response
        profile_info = {
            "uid": profile.uid,
            "email": profile.email,
            "username": profile.username,
            "date": profile.date,
        }
        return JsonResponse({"status": 200, "profile": profile_info}, status=200)

    except Exception as e:
        return JsonResponse(
            {"status": 500, "message": f"內部錯誤: {str(e)}"}, status=500
        )


@csrf_exempt
def login_view(request):
    if request.method == "POST" and request.content_type == "application/json":
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        users = Profile.objects.filter(username=username)
        if not users.exists():
            return JsonResponse(
                {"status": 400, "success": False, "message": "用戶不存在"}, status=400
            )
        user = users.first()
        if user.authenticate(password):
            request.session["uid"] = str(user.uid)
            return JsonResponse(
                {
                    "status": 200,
                    "message": "登入成功",
                    "success": True,
                    "uid": user.uid,
                },
                status=200,
            )
        else:
            return JsonResponse(
                {"status": 401, "success": False, "message": "Invalid credentials"},
                status=401,
            )
    else:
        return HttpResponseNotAllowed(["POST"])


@csrf_exempt
def logout_view(request):
    if "uid" in request.session:
        del request.session["uid"]
    return JsonResponse({"status": 200, "message": "已成功登出"}, status=200)


@login_required
@require_http_methods(["GET"])
def get_information(request):
    user_id = request.GET.get("uid")
    if not user_id:
        return JsonResponse({"status": 400, "message": "缺少用戶ID參數"}, status=400)

    try:
        user = Profile.objects.get(uid=user_id)
        user_info = {
            "username": user.username,
            "email": user.email,
        }
        return JsonResponse({"status": "success", "data": user_info}, status=200)

    except Profile.DoesNotExist:
        return JsonResponse({"status": "error", "message": "用戶不存在"}, status=404)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@csrf_exempt
def check(request, token):  # 信箱驗證
    if request.method == "POST":
        try:
            data = json.loads(bytes.decode(request.body, "utf-8"))
            token_use = email_token()
            email = token_use.confirm_token(token)  # 確認 token 並獲取 email

            if email is None:
                return JsonResponse(
                    {"status": "1", "message": "Invalid token"}, status=400
                )
            print("Email:" + email)

            user = Profile.objects.get(email=email)
            user.is_active = True  # 將用戶設置為活躍狀態
            user.save()
            message = {"status": "0", "message": "Email verified successfully"}
        except Profile.DoesNotExist:
            message = {"status": "1", "message": "User not found"}
        except Exception as e:
            print(e)
            message = {"status": "1", "message": "Error occurred during verification"}

        return JsonResponse(message)
