from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core import serializers
import json
from administrator.models import Administrator
from cafeInfo.models import Cafe
from user.models import Profile
from .decorators import admin_required


@csrf_exempt
@require_http_methods(["POST"])
def addAdministrator(request):
    try:
        data = json.loads(request.body)

        if Administrator.objects.filter(email=data["email"]).exists():
            return JsonResponse({'message': '此電子郵件已被其他管理者使用', "adminId": None}, status=400)
        if Administrator.objects.filter(admin_name=data["adminName"]).exists():
            return JsonResponse({'message': '此名稱已被其他管理者使用', "adminId": None}, status=400)

        user_profile = Profile.objects.get(uid=data["userId"])
        admin = Administrator(
            admin_name=data["adminName"], email=data["email"], admin_uid=user_profile)
        admin.set_password(data["password"])
        admin.save()
        return JsonResponse({"message": "Administrator created successfully.",
                             "adminId": str(admin.admin_uid)}, status=201)

    except Profile.DoesNotExist:
        return JsonResponse({"message": "Profile not found.", "adminId": None}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"message": "Invalid JSON.", "adminId": None}, status=400)
    except Exception as e:
        return JsonResponse({"message": str(e), "adminId": None}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def loginAdministrator(request):
    try:
        data = json.loads(request.body)
        admin_name = data["adminName"]
        password = data["password"]

        try:
            admin = Administrator.objects.get(admin_name=admin_name)
        except Administrator.DoesNotExist:
            return JsonResponse({"message": "Administrator not found."}, status=404)

        if admin.check_password(password):
            return JsonResponse({"message": "Login successful."}, status=200)
        else:
            return JsonResponse({"message": "Invalid password."}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({"message": "Invalid JSON."}, status=400)
    except Exception as e:
        return JsonResponse({"message": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def deleteAdministrator(request):
    try:
        data = json.loads(request.body)
        admin_uid = data["adminId"]
        admin = Administrator.objects.get(admin_uid=admin_uid)
        admin.delete()

        return JsonResponse({"message": "Administrator deleted successfully."}, status=200)

    except Administrator.DoesNotExist:
        return JsonResponse({"message": "Administrator not found."}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"message": "Invalid JSON."}, status=400)
    except Exception as e:
        return JsonResponse({"message": str(e)}, status=500)


@admin_required()
@csrf_exempt
@require_http_methods(["POST"])
def deleteCafe(request):
    try:
        data = json.loads(request.body)
        cafe = Cafe.objects.get(cafe_id=data["cafeId"])
        cafe.delete()
        return JsonResponse({"message": "Cafe deleted successfully.", "success": True}, status=200)

    except Cafe.DoesNotExist:
        return JsonResponse({"message": "Cafe not found.", "success": False}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"message": "Invalid JSON.", "success": False}, status=400)
    except Exception as e:
        return JsonResponse({"message": str(e), "success": False}, status=500)


@admin_required()
@csrf_exempt
@require_http_methods(["PUT"])
def judgeCafe(request):
    try:
        data = json.loads(request.body)
        cafe = Cafe.objects.get(cafe_id=data['cafeId'])
        cafe.legal = data['isLegal']
        cafe.save()
        return JsonResponse({"message": "Cafe updated successfully.", "success": True}, status=200)

    except Cafe.DoesNotExist:
        return JsonResponse({"message": "Cafe not found.", "success": False}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"message": "Invalid JSON.", "success": False}, status=400)
    except Exception as e:
        return JsonResponse({"message": str(e), "success": False}, status=500)


@admin_required()
@csrf_exempt
@require_http_methods(["GET"])
def getJudgedCafes(request):
    try:
        # 找出所有legal 欄位非空的咖啡廳
        cafe_list = Cafe.objects.exclude(legal=None)
        cafe_list_json = []
        for cafe in cafe_list:
            cafe_list_json.append({"cafeId": str(
                cafe.cafe_id), "cafeName": cafe.cafe_name, "isLegal": cafe.legal, "userId": str(cafe.owner.uid)})
        return JsonResponse({"cafeList": cafe_list_json, "success": True}, status=200)

    except Exception as e:
        return JsonResponse({"message": str(e), "success": False}, status=500)


@admin_required()
@csrf_exempt
@require_http_methods(["GET"])
def getUnjudgedCafes(request):
    try:
        # 找出所有legal 欄位為空的咖啡廳
        cafe_list = Cafe.objects.filter(legal=None)
        cafe_list_json = []
        for cafe in cafe_list:
            cafe_list_json.append(
                {"cafeId": str(cafe.cafe_id), "cafeName": cafe.cafe_name, "userId": str(cafe.owner.uid)})
        return JsonResponse({"cafeList": cafe_list_json, "success": True}, status=200)

    except Exception as e:
        return JsonResponse({"message": str(e), "success": False}, status=500)


@admin_required()
@csrf_exempt
@require_http_methods(["GET"])
def getUnjudgedCafesList(request):
    try:
        cafe_list = Cafe.objects.filter(legal=None)
        cafe_list_json = []
        for cafe in cafe_list:
            cafe_list_json.append(
                {"cafeId": str(cafe.cafe_id), "cafeName": cafe.cafe_name, "isLegal": cafe.legal, "userId": str(cafe.owner.uid)})
        return JsonResponse({"cafeList": cafe_list_json, "success": True}, status=200)

    except Exception as e:
        return JsonResponse({"message": str(e), "success": False}, status=500)


@admin_required()
@csrf_exempt
@require_http_methods(["GET"])
def getAllUsers(request):
    try:
        user_list = Profile.objects.all()
        user_list_json = []
        for user in user_list:
            user_list_json.append({"userId": str(
                user.uid), "userName": user.username, "email": user.email, "phone": user.phone})
        return JsonResponse({"userList": user_list_json, "success": True}, status=200)

    except Exception as e:
        return JsonResponse({"message": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def checkIsAdmin(request):
    try:
        userId = request.GET.get("userId")
        admin = Administrator.objects.get(admin_uid=userId)
        return JsonResponse({"isAdmin": True, "success": True}, status=200)
    except Administrator.DoesNotExist:
        return JsonResponse({"isAdmin": False, "success": True}, status=200)
    except Exception as e:
        return JsonResponse({"message": str(e), "success": False}, status=500)
    
@admin_required()
@csrf_exempt
@require_http_methods(["POST"])
def deleteUser(request):
    try:
        data = json.loads(request.body)
        user_profile = Profile.objects.get(uid=data["userId"])
        user_profile.delete()
        return JsonResponse({"message": "User deleted successfully.", "success": True}, status=200)

    except Profile.DoesNotExist:
        return JsonResponse({"message": "User not found.", "success": False}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({"message": "Invalid JSON.", "success": False}, status=400)
    except Exception as e:
        return JsonResponse({"message": str(e), "success": False}, status=500)
    
@login_required
@csrf_exempt
def add_new_cafe(request):
    if request.method == 'POST':
        try:
            owner = Profile.objects.get(uid=admin_uid)
        except Profile.DoesNotExist:
            return JsonResponse({'status': 404, 'message': '找不到用戶'}, status=404)

        try:
            # 假設 Cafe 中有一個外鍵指向 User 模型
            cafe = Cafe.objects.create(
                                     )
            cafe.save()
            
            if 'images' in request.FILES:
                for image in request.FILES.getlist('images'):
                    CafeImage.objects.create(cafe=cafe, image=image)
            cafe_images = CafeImage.objects.filter(cafe=cafe)
            images_urls = [image.image.url for image in cafe_images]

            cafe_info = {
                
            }
            
            cafe.save()
            return JsonResponse({'status': 200, 'success': True, 'cafe_info': cafe_info}, status=200)

        except Exception as e:
            return JsonResponse({'status': 500, 'success': False, 'message': str(e)}, status=500)

    else:
        # return HttpResponseNotAllowed(['POST'])
        return JsonResponse({'status': 400, 'success': False, 'message': '只接受 POST 請求'}, status=400)

@login_required
@csrf_exempt
def delete_cafe(request):
    if request.method == 'POST':
        ownerId = request.POST['ownerId']
        cafeId = request.POST['cafeId']
        # 驗證和處理輸入...

        try:
            cafe = Cafe.objects.get(cafe_id=cafeId)  
            cafe.delete()
            return JsonResponse({'status': 200, 'success': True, 'message': '咖啡廳刪除成功'}, status=200)
        
        except Cafe.DoesNotExist:
            return JsonResponse({'status': 404, 'success': False, 'message': '咖啡廳不存在'}, status=404)
        
        except Exception as e:
            return JsonResponse({'status': 500, 'success': False, 'message': str(e)}, status=500)

    return JsonResponse({'status': 400, 'success': False, 'message': '只接受POST請求'}, status=400)

@login_required
@csrf_exempt
def update_cafe(request):
    if request.method == 'POST':
        admin_uid = request.POST.get('ownerId')
        cafe_id = request.POST.get('cafeId')

        if not admin_uid or not cafe_id:
            return JsonResponse({'status': 400, 'success': False, 'message': '管理員 id 或咖啡廳 id 未填寫'}, status=400)

        cafe = Cafe.objects.filter(owner__uid=admin_uid, cafe_id=cafe_id).first()
        if not cafe:
            return JsonResponse({'status': 404, 'success': False, 'message': '咖啡廳不存在'}, status=404)

        # 需要加上 get cafe 的所有參數
        cafe_name = request.POST.get('name', cafe.name)
        

        try:
            owner = Profile.objects.get(uid=admin_uid)
        except Profile.DoesNotExist:
            return JsonResponse({'status': 404, 'message': '找不到用戶'}, status=404)
        
        try:
            cafe = Cafe.objects.get(cafe_id=cafe_id)
            # 放上 cafe 的參數
            # ex: cafe.cafe_name = name
            
            cafe.save()  
        
            if 'images' in request.FILES:
                # 刪除原有的圖片
                CafeImage.objects.filter(cafe=cafe).delete()
                
                # 新增新的圖片
                for image in request.FILES.getlist('images'):
                    CafeImage.objects.create(cafe=cafe, image=image)

            cafe_images = CafeImage.objects.filter(cafe=cafe)
            images_urls = [image.image.url for image in cafe_images]

            cafe_info = {
                # 放上 cafe 的所有資訊
            }
            return JsonResponse({'status': 200, 'success': True, 'cafe_info': cafe_info}, status=200)
        
        except Cafe.DoesNotExist:
            return JsonResponse({'status': 404, 'success': False, 'message': '咖啡廳不存在'}, status=404)
        
        except Exception as e:
            return JsonResponse({'status': 500, 'success': False, 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 400, 'success': False, 'message': '只接受POST請求'}, status=400)