import json
from django.http import HttpResponseNotAllowed, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Profile
from cafeInfo import Cafe, CafeImage
from .decorators import login_required

@csrf_exempt
def user_signup(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    try:
        data = json.loads(request.body)
        email = data.get("email")
        username = data.get("username")
        password = data.get("password")

        # 驗證必填欄位
        if not all([email, username, password]):
            return JsonResponse({'success': False, 'err': '缺少必要的參數'}, status=400)

        # 驗證密碼規則
        validate_password(password)

        # 驗證唯一性
        if Profile.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'err': '電子郵件已存在'}, status=400)
        if Profile.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'err': '用戶名已存在'}, status=400)

        # 創建用戶
        encrypted_password = make_password(password)
        profile = Profile.objects.create(email=email, username=username, password=encrypted_password)

        return JsonResponse({'success': True, 'userId': profile.uid}, status=200)

    except ValidationError as e:
        return JsonResponse({'success': False, 'err': e.messages}, status=400)

    except Exception as e:
        return JsonResponse({'success': False, 'err': str(e)}, status=500)


@csrf_exempt
def user_login(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        # 驗證參數
        if not username or not password:
            return JsonResponse({'success': False, 'err': '缺少必要的參數'}, status=400)

        # 驗證用戶
        user = Profile.objects.filter(username=username).first()
        if user and check_password(password, user.password):
            request.session['uid'] = str(user.uid)
            return JsonResponse({'success': True}, status=200)

        return JsonResponse({'success': False, 'err': '用戶名或密碼錯誤'}, status=401)

    except Exception as e:
        return JsonResponse({'success': False, 'err': str(e)}, status=500)


@login_required
def get_userinfo(request):
    if request.method != 'GET':
        return HttpResponseNotAllowed(['GET'])

    userId = request.GET.get('userId')
    if not userId:
        return JsonResponse({'success': False, 'err': '缺少用戶ID參數'}, status=400)

    try:
        user = Profile.objects.get(uid=userId)
        user_info = {
            'username': user.username,
            'email': user.email,
            'cafes': []
        }

        cafes = Cafe.objects.filter(owner=user)
        for cafe in cafes:
            cafe_images = CafeImage.objects.filter(cafe=cafe)
            images_urls = [image.image.url for image in cafe_images]
            user_info['cafes'].append({
                'name': cafe.name,
                'address': cafe.address,
                'images': images_urls
            })

        return JsonResponse({'success': True, 'data': user_info}, status=200)

    except Profile.DoesNotExist:
        return JsonResponse({'success': False, 'err': '用戶不存在'}, status=404)

    except Exception as e:
        return JsonResponse({'success': False, 'err': str(e)}, status=500)
