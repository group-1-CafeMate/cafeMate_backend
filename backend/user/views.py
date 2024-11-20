import json
from django.http import HttpResponseNotAllowed, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Profile
from cafeInfo import Cafe, CafeImage
from .decorators import login_required

@csrf_exempt
def user_signup(request):
    if request.method == 'POST':
        try:
            # 使用 JSON 格式提取數據
            data = json.loads(request.body)
            email = data.get("email")
            username = data.get("username")
            password = data.get("password")

            # 驗證所有必要欄位是否存在
            if not all([email, username, password]):
                return JsonResponse({
                    'status': 400,
                    'success': False,
                    'err': '缺少必要的參數'
                }, status=400)

            # 驗證密碼是否符合要求
            validate_password(password)

            # 加密密碼
            encrypted_password = make_password(password)

            # 檢查用戶名和電子郵件的唯一性
            if Profile.objects.filter(email=email).exists():
                return JsonResponse({
                    'status': 400,
                    'success': False,
                    'err': '電子郵件已存在'
                }, status=400)
            if Profile.objects.filter(username=username).exists():
                return JsonResponse({
                    'status': 400,
                    'success': False,
                    'err': '用戶名已存在'
                }, status=400)

            # 創建用戶資料
            profile = Profile.objects.create(
                email=email, username=username, password=encrypted_password)
            
            # 成功回應，回傳 userId
            return JsonResponse({
                'status': 200,
                'success': True,
                'userId': profile.uid,
                'err': None
            }, status=200)

        except ValidationError as e:
            # 密碼驗證失敗
            return JsonResponse({
                'status': 400,
                'success': False,
                'err': e.messages
            }, status=400)

        except Exception as e:
            # 其他錯誤
            return JsonResponse({
                'status': 500,
                'success': False,
                'err': str(e)
            }, status=500)
    else:
        return HttpResponseNotAllowed(['POST'])


@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        try:
            # 提取 JSON 格式的資料
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            # 檢查必要參數是否存在
            if not username or not password:
                return JsonResponse({
                    'status': 400,
                    'success': False,
                    'err': '缺少必要的參數'
                }, status=400)

            # 查詢用戶是否存在
            users = Profile.objects.filter(username=username)
            if users.exists():
                user = users.first()
                # 驗證密碼
                if check_password(password, user.password):
                    request.session['uid'] = str(user.uid)
                    return JsonResponse({
                        'status': 200,
                        'success': True,
                        'err': None  # 成功時 err 設為 None
                    }, status=200)
                else:
                    # 密碼錯誤
                    return JsonResponse({
                        'status': 401,
                        'success': False,
                        'err': '密碼不正確'
                    }, status=401)
            else:
                # 用戶不存在
                return JsonResponse({
                    'status': 400,
                    'success': False,
                    'err': '用戶不存在'
                }, status=400)
                
        except Exception as e:
            # 其他錯誤
            return JsonResponse({
                'status': 500,
                'success': False,
                'err': str(e)
            }, status=500)
    else:
        return HttpResponseNotAllowed(['POST'])

@login_required
@require_http_methods(["GET"])
def get_userinfo(request):
    userId = request.GET.get('userId')  # 使用規格書中的參數名稱
    if not userId:
        return JsonResponse({'status': 400, 'success': False, 'err': '缺少用戶ID參數'}, status=400)

    try:
        user = Profile.objects.get(uid=userId)
        user_info = {
            'username': user.username,
            'email': user.email,
        }

        cafes = Cafe.objects.filter(owner=user)
        cafe_info_list = []
        for cafe in cafes:
            cafe_images = CafeImage.objects.filter(cafe=cafe)
            images_urls = [image.image.url for image in cafe_images]

            # 根據需求添加需要的咖啡店資訊
            cafe_info = {
                'name': cafe.name,
                'address': cafe.address,
                'images': images_urls
            }
            cafe_info_list.append(cafe_info)

        user_info['cafes'] = cafe_info_list

        return JsonResponse({'status': 200, 'success': True, 'data': user_info}, status=200)

    except Profile.DoesNotExist:
        return JsonResponse({'status': 404, 'success': False, 'err': '用戶不存在'}, status=404)

    except Exception as e:
        return JsonResponse({'status': 500, 'success': False, 'err': str(e)}, status=500)