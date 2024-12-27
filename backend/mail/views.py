from .tasks import send_custom_email
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def send_email_view(request):
    if request.method == "GET":  # 改為處理 GET 請求
        try:
            email = request.GET.get("email")  # 取得查詢字串中的 email
            name = request.GET.get("name")  # 取得查詢字串中的 name
            print("email: ", email)
            print("name: ", name)

            if not email or not name:
                return JsonResponse(
                    {"status": 400, "message": "Missing email or name in the request."},
                    status=400,
                )

            send_custom_email(email, name)
            return JsonResponse({"status": 200, "message": "Email sent successfully!"})
        except Exception as e:
            return JsonResponse(
                {"status": 500, "message": f"Error occurred: {str(e)}"}, status=500
            )
    else:
        return JsonResponse(
            {"status": 405, "message": "Only GET requests are allowed."}, status=405
        )
