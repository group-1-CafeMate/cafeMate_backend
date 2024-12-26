from django.http import JsonResponse


def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if "uid" in request.session:
            return view_func(request, *args, **kwargs)
        else:
            return JsonResponse({"status": 403, "message": "用戶未登入"}, status=403)

    return wrapper
