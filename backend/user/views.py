from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import check_password, make_password
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
# from django.contrib.auth.models import User
from user.decorators import login_required

from .models import Profile
from cafeInfo import Cafe, CafeImage
from .decorators import login_required
# Create your views here.

@csrf_exempt
def sign_up(request):
    if request.method == 'POST':
        try:
            email = request.POST["email"]
            username = request.POST["username"]
            password = request.POST["password"]

            validate_password(password)  # 驗證密碼是否符合要求

            encrypted_password = make_password(password)  # 加密密碼

            # 用戶名和電子郵件不能重複
            if Profile.objects.filter(email=email).exists():
                return JsonResponse({'status': 400, 'message': '電子郵件已存在'}, status=400)
            if Profile.objects.filter(username=username).exists():
                return JsonResponse({'status': 400, 'message': '用戶名已存在'}, status=400)

            profile = Profile.objects.create(
                email=email, username=username, password=encrypted_password)
            profile.save()

            profile_info = {
                'uid': profile.uid,
                'email': profile.email,
                'username': profile.username,
                'date': profile.date,
            }
            return JsonResponse({'status': 200, 'profile': profile_info}, status=200)

        except ValidationError as e:
            return JsonResponse({'status': 400, 'message': e.messages}, status=400)

        except Exception as e:
            return JsonResponse({'status': 500, 'message': str(e)}, status=500)
    else:
        return HttpResponseNotAllowed(['POST'])


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        users = Profile.objects.filter(username=username)
        if users.exists():
            user = users.first()
            if user.authenticate(password):
                request.session['uid'] = str(user.uid)
                return JsonResponse({'status': 200, 'message': '登入成功', 'success': True, 'uid': user.uid}, status=200)
            else:
                return JsonResponse({'status': 401,  'success': False, 'message': 'Invalid credentials'}, status=401)
        else:
            return JsonResponse({'status': 400,  'success': False, 'message': '用戶不存在'}, status=400)
    else:
        return HttpResponseNotAllowed(['POST'])
    
@login_required
@require_http_methods(["GET"])
def get_information(request):
    if request.method == 'GET':
        userId = request.GET['uid']
        if not userId:
            return JsonResponse({'status': 400, 'message': '缺少用戶ID參數'}, status=400)

        try:
            user = Profile.objects.get(uid=userId)
            user_info = {
                'username': user.username,
                'email': user.email,
            }
            # cafes = Cafe.objects.filter(owner=user)
            cafe_info_list = []
            for cafe in cafes:

                cafe_images = CafeImage.objects.filter(cafe=cafe)
                images_urls = [image.image.url for image in cafe_images]

                cafe_info = {
                    
                }
                cafe_info_list.append(cafe_info)

            user_info['cafes'] = cafe_info_list
            return JsonResponse({'status': 'success', 'data': user_info}, status=200)
        
        except Profile.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '用戶不存在'}, status=404)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    else:
        # return HttpResponseNotAllowed(['POST'])
        return JsonResponse({'status': 400, 'success': False, 'message': '只接受GET請求'}, status=400)

