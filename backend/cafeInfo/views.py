from user.decorators import login_required
from .models import Cafe, CafeImage, MetroStation
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .utils import calculate_and_sort_cafes, LatitudeLongitude, generate_image_url


from django.shortcuts import get_object_or_404
from django.middleware.csrf import CsrfViewMiddleware


def debug_csrf_token(request):
    csrf_header = request.META.get("HTTP_X_CSRFTOKEN")
    csrf_cookie = request.COOKIES.get("csrftoken")

    print("CSRF Header:", csrf_header)
    print("CSRF Cookie:", csrf_cookie)

    # 驗證 CSRF
    try:
        CsrfViewMiddleware().process_view(request, None, None, None)
        print("CSRF Validation Passed")
    except Exception as e:
        print("CSRF Validation Error:", e)
        return JsonResponse({"error": "CSRF validation failed"}, status=403)


@login_required
@require_http_methods(["GET"])
def get_all_cafes(request):
    try:
        user_lat, user_lon = None, None
        # 先檢查是否有傳入 metro_station_id
        metro_station_id = request.GET.get("metro_station_id")
        if metro_station_id:
            try:
                # 從 MetroStation 模型取得經緯度
                metro_station = get_object_or_404(
                    MetroStation, metro_station_id=metro_station_id
                )
                user_lat = metro_station.latitude
                user_lon = metro_station.longitude
            except Exception as e:
                return JsonResponse(
                    {
                        "message": f"Invalid metro_station_id: {str(e)}",
                        "success": False,
                    },
                    status=400,
                )
        # 如果沒有 metro_station_id，則使用用戶提供的經緯度
        user_lat = request.GET.get("latitude")
        user_lon = request.GET.get("longitude")
        has_latlon = user_lat and user_lon
        # 檢查經緯度是否合理
        user_location = None
        if has_latlon:
            try:
                user_lat = float(user_lat)
                user_lon = float(user_lon)
                user_location = LatitudeLongitude(user_lat, user_lon)
            except ValueError as e:
                return JsonResponse(
                    {
                        "message": f"Invalid latitude or longitude: {str(e)}",
                        "success": False,
                    },
                    status=400,
                )

        cafes = Cafe.objects.filter(legal=True)
        if not cafes.exists():
            return JsonResponse(
                {"message": "No cafes found", "success": False}, status=404
            )

        # 計算並排序咖啡廳
        cafes_with_distance = calculate_and_sort_cafes(cafes, user_location)

        # 格式化為包含所需資訊的列表
        cafe_info = []
        for distance, cafe in cafes_with_distance:
            images_urls = [
                generate_image_url(request, img.image.url) for img in cafe.images.all()
            ]  # 提取所有圖片 URL
            open_hour_list = cafe.get_open_hour_list()
            cafe_info.append(
                {
                    "cafe_id": str(cafe.cafe_id),
                    "name": cafe.name,
                    "phone": cafe.phone,
                    "addr": cafe.addr,
                    "work_and_study_friendly": cafe.work_and_study_friendly,
                    "rating": cafe.rating,
                    "time_unlimit": cafe.time_unlimit,
                    "socket": cafe.socket,
                    "pets_allowed": cafe.pets_allowed,
                    "wiFi": cafe.wiFi,
                    "open_hour": open_hour_list,
                    "distance": distance,
                    "info": cafe.info,
                    "comment": cafe.comment,
                    "ig_link": cafe.ig_link,
                    "images_urls": images_urls,  # 包含所有圖片 URL
                }
            )

        return JsonResponse(
            {"cafes": cafe_info, "success": True}, safe=False, status=200
        )

    except Exception as e:
        return JsonResponse({"message": str(e), "success": False}, status=500)


# 只有一間不用排序
@login_required
@require_http_methods(["GET"])
def get_cafe(request):
    cafe_id = request.GET.get("cafe_id", None)

    if not cafe_id:
        return JsonResponse(
            {"message": "Missing cafe_id parameter", "success": False}, status=400
        )

    try:
        cafe = Cafe.objects.get(cafe_id=cafe_id)
        cafe_images = CafeImage.objects.filter(cafe=cafe)
        images_urls = [
            generate_image_url(request, image.image.url) for image in cafe_images
        ]

        open_hour_list = cafe.get_open_hour_list()
        cafe_info = {
            "cafe_id": str(cafe.cafe_id),
            "name": cafe.name,
            "phone": cafe.phone,
            "addr": cafe.addr,
            "work_and_study_friendly": cafe.work_and_study_friendly,
            "rating": cafe.rating,
            "time_unlimit": cafe.time_unlimit,
            "socket": cafe.socket,
            "pets_allowed": cafe.pets_allowed,
            "wiFi": cafe.wiFi,
            "open_hour": open_hour_list,
            "info": cafe.info,
            "comment": cafe.comment,
            "ig_link": cafe.ig_link,
            "gmap_link": cafe.gmap_link,
            "images_urls": images_urls,
        }
        return JsonResponse({"cafe": cafe_info, "success": True}, status=200)

    except Cafe.DoesNotExist:
        return JsonResponse({"message": "Cafe not found", "success": False}, status=404)

    except Exception as e:
        return JsonResponse({"message": str(e), "success": False}, status=500)


@login_required
@require_http_methods(["GET"])
def filter_cafes_by_labels(request):
    filters = {
        "work_and_study_friendly": request.GET.get("work_and_study_friendly"),
        "socket": request.GET.get("socket"),
        "time_unlimit": request.GET.get("time_unlimit"),
        "wiFi": request.GET.get("wifi"),
        "pets_allowed": request.GET.get("pets_allowed"),
    }

    filters = {key: True for key, value in filters.items() if value == "true"}

    # 先檢查是否有傳入 metro_station_id
    metro_station_id = request.GET.get("metro_station_id")
    user_lat, user_lon = None, None
    if metro_station_id:
        try:
            # 從 MetroStation 模型取得經緯度
            metro_station = get_object_or_404(
                MetroStation, metro_station_id=metro_station_id
            )
            user_lat = metro_station.latitude
            user_lon = metro_station.longitude
        except Exception as e:
            return JsonResponse(
                {"message": f"Invalid metro_station_id: {str(e)}", "success": False},
                status=400,
            )
    else:
        # 如果沒有 metro_station_id，則檢查用戶傳入的經緯度
        user_lat = request.GET.get("latitude")
        user_lon = request.GET.get("longitude")

    user_location = None
    has_latlon = user_lat and user_lon
    if has_latlon:
        try:
            user_lat = float(user_lat)
            user_lon = float(user_lon)
            user_location = LatitudeLongitude(user_lat, user_lon)
        except ValueError as e:
            return JsonResponse(
                {
                    "message": f"Invalid latitude or longitude: {str(e)}",
                    "success": False,
                },
                status=400,
            )
    try:
        cafes = Cafe.objects.filter(legal=True, **filters)
        if not cafes:
            return JsonResponse(
                {"message": "No cafes match the given labels", "success": False},
                status=404,
            )
        cafes_with_distance = calculate_and_sort_cafes(cafes, user_location)
        partial_cafe_info = []
        for distance, cafe in cafes_with_distance:
            open_hour_list = cafe.get_open_hour_list()
            partial_cafe_info.append(
                {
                    "cafe_id": str(cafe.cafe_id),
                    "name": cafe.name,
                    "rating": cafe.rating,
                    "open_hour": open_hour_list,
                    "distance": distance,
                    "labels": cafe.get_labels(),
                    "image_url": (
                        generate_image_url(request, cafe.images.all()[0].image.url)
                        if cafe.images.exists()
                        else None
                    ),
                }
            )

        return JsonResponse(
            {"cafes": partial_cafe_info, "success": True}, safe=False, status=200
        )

    except Exception as e:
        return JsonResponse({"message": str(e), "success": False}, status=500)


@login_required
@require_http_methods(["GET"])
def get_top_cafes(request):
    try:
        # 先檢查是否有傳入 metro_station_id
        metro_station_id = request.GET.get("metro_station_id")
        user_lat, user_lon = None, None
        if metro_station_id:
            try:
                # 從 MetroStation 模型取得經緯度
                metro_station = get_object_or_404(
                    MetroStation, metro_station_id=metro_station_id
                )
                user_lat = metro_station.latitude
                user_lon = metro_station.longitude
            except Exception as e:
                return JsonResponse(
                    {
                        "message": f"Invalid metro_station_id: {str(e)}",
                        "success": False,
                    },
                    status=400,
                )

        # 如果沒有 metro_station_id，則檢查用戶傳入的經緯度
        user_lat = request.GET.get("latitude")
        user_lon = request.GET.get("longitude")
        has_latlon = user_lat and user_lon
        user_location = None
        if has_latlon:
            # 如果經度、緯度不合理
            try:
                user_lat = float(user_lat)
                user_lon = float(user_lon)
                user_location = LatitudeLongitude(user_lat, user_lon)

            except ValueError as e:
                return JsonResponse(
                    {
                        "message": f"Invalid latitude or longitude: {str(e)}",
                        "success": False,
                    },
                    status=400,
                )
        # 按照 ig_post_cnt 降序("-"表降序)排列，取前六名
        top_cafes = Cafe.objects.filter(legal=True).order_by("-ig_post_cnt")[:6]

        if not top_cafes.exists():
            return JsonResponse(
                {"message": "No cafes found", "success": False}, status=404
            )

        partial_cafe_info = [
            {
                "cafe_id": str(cafe.cafe_id),
                "name": cafe.name,
                "rating": cafe.rating,
                "open_hour": cafe.get_open_hour_list(),
                "distance": (
                    -1
                    if user_location is None
                    else user_location.distance_to(
                        LatitudeLongitude(cafe.latitude, cafe.longitude)
                    )
                ),
                "labels": cafe.get_labels(),
                "image_url": (
                    generate_image_url(request, cafe.images.all()[0].image.url)
                    if cafe.images.exists()
                    else None
                ),
                "ig_post_count": cafe.ig_post_cnt,
            }
            for cafe in top_cafes
        ]

        return JsonResponse(
            {"cafes": partial_cafe_info, "success": True}, safe=False, status=200
        )

    except Exception as e:
        return JsonResponse({"message": str(e), "success": False}, status=500)


@require_http_methods(["GET"])
def get_all_metro_stations(request):
    metro_stations = MetroStation.objects.all().values("metro_station_id", "name")
    return JsonResponse(list(metro_stations), safe=False)
