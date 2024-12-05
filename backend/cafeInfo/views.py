from django.shortcuts import render
from .models import Cafe, CafeImage
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def get_all_cafes(request):
    try:
        cafes = Cafe.objects.filter(legal=True)

        if not cafes.exists():
            return JsonResponse({'message': 'No cafes found', 'success': False}, status = 404)
        
        partial_cafe_info = [{
            'cafe_id': str(cafe.cafe_id),
            'name': cafe.name,
            'grade': cafe.grade,
            'open_hour': cafe.open_hour,
            'open_now': cafe.open_now,
            'distance': cafe.distance,
            'labels': cafe.get_labels(),
            'image_url': cafe.images.all()[0].image.url if cafe.images.exists() else None
            }
            for cafe in cafes
        ]

        return JsonResponse({'cafes': partial_cafe_info, 'success': True}, safe=False, status = 200) 
    
    except Exception as e:
        return JsonResponse({"message": str(e), 'success': False}, status=500)

@require_http_methods(["GET"])
def get_cafe(request):
    cafe_id = request.GET.get('cafe_id', None)
    
    if not cafe_id:
        return JsonResponse({'message': 'Missing cafe_id parameter', 'success': False}, status=400)

    try:
        cafe = Cafe.objects.get(cafe_id=cafe_id)
        cafe_images = CafeImage.objects.filter(cafe=cafe)
        images_urls = [image.image.url for image in cafe_images]
        
        cafe_info = {
            'cafe_id': str(cafe.cafe_id),
            'name': cafe.name,
            'phone': cafe.phone,
            'addr': cafe.addr,
            'quiet': cafe.quiet,
            'grade': cafe.grade,
            'time_unlimit': cafe.time_unlimit,
            'time_limit': cafe.time_limit,
            'socket': cafe.socket,
            'pets_allowed': cafe.pets_allowed,
            'wiFi': cafe.wiFi,
            'open_hour': cafe.open_hour,
            'open_now': cafe.open_now,
            'distance': cafe.distance,
            'info': cafe.info,
            'comment': cafe.comment,
            'ig_link': cafe.ig_link,
            'fb_link': cafe.fb_link,
            'images_urls': images_urls,
        }

        return JsonResponse({'cafe': cafe_info, 'success': True}, status = 200)
    
    except Cafe.DoesNotExist:
        return JsonResponse({'message': 'Cafe not found', 'success': False},  status = 404)
    
    except Exception as e:
        return JsonResponse({"message": str(e), "success": False}, status = 500)

@require_http_methods(["GET"])
def get_top_cafes(request):
    try:
        # 按照 ig_post_cnt 降序("-"表降序)排列，取前六名
        top_cafes = Cafe.objects.filter(legal=True).order_by('-ig_post_cnt')[:6]

        if not top_cafes.exists():
            return JsonResponse({'message': 'No cafes found', 'success': False}, status=404)

        partial_cafe_info = [
            {
                'cafe_id': str(cafe.cafe_id),
                'name': cafe.name,
                'grade': cafe.grade,
                'open_hour': cafe.open_hour,
                'open_now': cafe.open_now,
                'distance': cafe.distance,
                'labels': cafe.get_labels(),
                'image_url': cafe.images.all()[0].image.url if cafe.images.exists() else None
            }
            for cafe in top_cafes
        ]

        return JsonResponse({'cafes': partial_cafe_info, 'success': True}, safe=False, status=200)

    except Exception as e:
        return JsonResponse({"message": str(e), 'success': False}, status=500)
