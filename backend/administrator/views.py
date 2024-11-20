import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from administrator.models import Administrator
from cafeInfo.models import Cafe
from user.models import Profile
from .decorators import admin_required

# 管理員刊登咖啡廳
@admin_required()
@csrf_exempt
@require_http_methods(["POST"])
def addNewCafe(request):
    try:
        data = json.loads(request.body)
        required_fields = [
            "adminId", "name", "phone", "addr", "quiet", "grade", 
            "cafeTimeLimit", "socket", "petsAllowed", "wiFi", 
            "openHour", "openNow", "distance", "info", "comment", 
            "igHashTagCnt", "googleReviewCnt", "IGLink", 
            "FBLink", "googleReviewLink"
        ]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return JsonResponse({
                'status': 400,
                'success': False,
                'err': f'缺少必要的參數: {", ".join(missing_fields)}'
            }, status=400)

        cafe = Cafe.objects.create(**{field: data[field] for field in required_fields})
        return JsonResponse({
            'status': 200,
            'success': True,
            'message': 'Cafe added successfully',
            'CafeId': cafe.cafe_id,
            'err': None
        }, status=200)

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 400,
            'success': False,
            'err': 'Invalid JSON format'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 500,
            'success': False,
            'err': 'Internal server error'
        }, status=500)

# 管理員更新咖啡廳
@admin_required()
@csrf_exempt
@require_http_methods(["PUT"])
def updateCafe(request):
    try:
        data = json.loads(request.body)
        cafe_id = data.get("cafeId")
        if not cafe_id:
            return JsonResponse({
                'status': 400,
                'success': False,
                'err': '缺少必要的參數: cafeId'
            }, status=400)

        try:
            cafe = Cafe.objects.get(cafe_id=cafe_id)
            for key, value in data.items():
                if hasattr(cafe, key):
                    setattr(cafe, key, value)
            cafe.save()

            return JsonResponse({
                'status': 200,
                'success': True,
                'message': 'Cafe updated successfully',
                'err': None
            }, status=200)
        except Cafe.DoesNotExist:
            return JsonResponse({
                'status': 404,
                'success': False,
                'err': '找不到指定的咖啡廳'
            }, status=404)

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 400,
            'success': False,
            'err': 'Invalid JSON format'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 500,
            'success': False,
            'err': 'Internal server error'
        }, status=500)

# 管理員刪除咖啡廳
@admin_required()
@csrf_exempt
@require_http_methods(["POST"])
def deleteCafe(request):
    try:
        data = json.loads(request.body)
        admin_id = data.get("adminId")
        cafe_id = data.get("cafeId")
        
        if not admin_id or not cafe_id:
            return JsonResponse({
                'status': 400,
                'success': False,
                'err': '缺少必要的參數: adminId 或 cafeId'
            }, status=400)

        try:
            cafe = Cafe.objects.get(cafe_id=cafe_id)
            cafe.delete()
            return JsonResponse({
                'status': 200,
                'success': True,
                'message': 'Cafe deleted successfully',
                'err': None
            }, status=200)
        except Cafe.DoesNotExist:
            return JsonResponse({
                'status': 404,
                'success': False,
                'err': '指定的咖啡廳不存在'
            }, status=404)

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 400,
            'success': False,
            'err': 'Invalid JSON format'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 500,
            'success': False,
            'err': 'Internal server error'
        }, status=500)

# 管理員審核咖啡廳
@admin_required()
@csrf_exempt
@require_http_methods(["PUT"])
def judgeCafe(request):
    try:
        data = json.loads(request.body)
        admin_id = data.get("adminId")
        cafe_id = data.get("cafeId")
        is_legal = data.get("isLegal", None)

        if not all([admin_id, cafe_id, is_legal is not None]):
            return JsonResponse({
                'status': 400,
                'success': False,
                'err': '缺少必要的參數: adminId, cafeId 或 isLegal'
            }, status=400)

        try:
            cafe = Cafe.objects.get(cafe_id=cafe_id)
            cafe.legal = is_legal
            cafe.save()
            return JsonResponse({
                'status': 200,
                'success': True,
                'message': 'Cafe updated successfully',
                'err': None
            }, status=200)
        except Cafe.DoesNotExist:
            return JsonResponse({
                'status': 404,
                'success': False,
                'err': '指定的咖啡廳不存在'
            }, status=404)

    except json.JSONDecodeError:
        return JsonResponse({
            'status': 400,
            'success': False,
            'err': 'Invalid JSON format'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 500,
            'success': False,
            'err': 'Internal server error'
        }, status=500)




   

# @csrf_exempt
# @require_http_methods(["POST"])
# def admin_signup(request):
#     try:
#         data = json.loads(request.body)

#         if Administrator.objects.filter(email=data["email"]).exists():
#             return JsonResponse({'message': '此電子郵件已被其他管理者使用', "adminId": None}, status=400)
#         if Administrator.objects.filter(admin_name=data["adminName"]).exists():
#             return JsonResponse({'message': '此名稱已被其他管理者使用', "adminId": None}, status=400)

#         user_profile = Profile.objects.get(uid=data["userId"])
#         admin = Administrator(
#             admin_name=data["adminName"], email=data["email"], admin_uid=user_profile)
#         admin.set_password(data["password"])
#         admin.save()
#         return JsonResponse({"message": "Administrator created successfully.",
#                              "adminId": str(admin.admin_uid)}, status=201)

#     except Profile.DoesNotExist:
#         return JsonResponse({"message": "Profile not found.", "adminId": None}, status=404)
#     except json.JSONDecodeError:
#         return JsonResponse({"message": "Invalid JSON.", "adminId": None}, status=400)
#     except Exception as e:
#         return JsonResponse({"message": str(e), "adminId": None}, status=500)


# @csrf_exempt
# @require_http_methods(["POST"])
# def admin_login(request):
#     try:
#         data = json.loads(request.body)
#         admin_name = data["adminName"]
#         password = data["password"]

#         try:
#             admin = Administrator.objects.get(admin_name=admin_name)
#         except Administrator.DoesNotExist:
#             return JsonResponse({"message": "Administrator not found."}, status=404)

#         if admin.check_password(password):
#             return JsonResponse({"message": "Login successful."}, status=200)
#         else:
#             return JsonResponse({"message": "Invalid password."}, status=400)

#     except json.JSONDecodeError:
#         return JsonResponse({"message": "Invalid JSON."}, status=400)
#     except Exception as e:
#         return JsonResponse({"message": str(e)}, status=500)
