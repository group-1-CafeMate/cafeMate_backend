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

        # 檢查用戶名和電子郵件是否重複
        if Profile.objects.filter(email=email).exists():
            return JsonResponse({"status": 400, "message": "電子郵件已存在"}, status=400)
        if Profile.objects.filter(username=username).exists():
            return JsonResponse({"status": 400, "message": "用戶名已存在"}, status=400)

        # 創建新用戶
        profile = Profile.objects.create(
            email=email,
            username=username,
            password=encrypted_password,
            email_verified=False,
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
        return JsonResponse({"status": 500, "message": f"內部錯誤: {str(e)}"}, status=500)


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
        if not user.email_verified:
            return JsonResponse(
                {"status": 400, "success": False, "message": "未驗證的電子郵件"},
                status=400,
            )
        if user.authenticate(password):
            request.session["uid"] = str(user.uid)

            response = JsonResponse(
                {
                    "status": 200,
                    "message": "登入成功",
                    "success": True,
                    "uid": user.uid,
                },
                status=200,
            )
            response.set_cookie(
                "sessionid",
                request.session.session_key,
                expires=3600 * 12,  # 12小時有效
            )
            return response
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
    if request.method == "GET":
        try:
            token_use = email_token()
            email = token_use.confirm_token(token)  # 確認 token 並獲取 email

            if email is None:
                return HttpResponse(
                    "<h1>Invalid or expired token</h1><p>Unable to verify your email. Please request a new verification link.</p>",
                    status=400,
                    content_type="text/html",
                )

            # 確保 Profile 存在並更新驗證狀態
            try:
                user = Profile.objects.get(email=email)
                if user.email_verified:
                    return HttpResponse(
                        "<h1>Email Already Verified</h1><p>Your email has already been verified. Thank you!</p>",
                        status=200,
                        content_type="text/html",
                    )

                user.email_verified = True
                user.save()

                return HttpResponse(
                    "<h1>Verification Successful</h1><p>Your email has been verified. Thank you for joining us!</p>",
                    status=200,
                    content_type="text/html",
                )
            except Profile.DoesNotExist:
                return HttpResponse(
                    "<h1>User Not Found</h1><p>The user associated with this token does not exist.</p>",
                    status=404,
                    content_type="text/html",
                )

        except Exception as e:
            print(f"Error: {e}")
            return HttpResponse(
                "<h1>Verification Failed</h1><p>An error occurred during verification. Please try again later.</p>",
                status=500,
                content_type="text/html",
            )

    return HttpResponse(
        "<h1>Invalid Request</h1><p>This endpoint only supports GET requests.</p>",
        status=405,
        content_type="text/html",
    )


# 重設密碼
@csrf_exempt
def reset_password(request):
    if request.method == "POST" and request.content_type == "application/json":
        try:
            # 確認用戶是否已登入
            if "uid" not in request.session:
                return JsonResponse(
                    {"status": 401, "message": "未登入，無法重設密碼"}, status=401
                )

            data = json.loads(request.body)
            uid = request.session["uid"]
            old_password = data.get("old_password")
            new_password = data.get("new_password")

            # 檢查必要字段
            if not old_password or not new_password:
                return JsonResponse({"status": 400, "message": "缺少必要字段"}, status=400)

            # 獲取用戶
            try:
                user = Profile.objects.get(uid=uid)
            except Profile.DoesNotExist:
                return JsonResponse({"status": 404, "message": "用戶不存在"}, status=404)

            # 驗證舊密碼是否正確
            if not user.authenticate(old_password):
                return JsonResponse({"status": 400, "message": "舊密碼不正確"}, status=400)

            # 驗證新密碼是否符合規範
            try:
                validate_password(new_password)
            except ValidationError as e:
                return JsonResponse({"status": 400, "message": e.messages}, status=400)

            # 更新密碼
            user.password = make_password(new_password)
            user.save()

            return JsonResponse({"status": 200, "message": "密碼已成功重設"}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"status": 400, "message": "請求不是有效的 JSON"}, status=400)
        except Exception as e:
            return JsonResponse(
                {"status": 500, "message": f"內部錯誤: {str(e)}"}, status=500
            )
    else:
        return HttpResponseNotAllowed(["POST"])
