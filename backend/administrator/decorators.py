from functools import wraps
from django.contrib import messages
from django.http import JsonResponse
from administrator.models import Administrator

def isAdmin(userId):
    if Administrator.objects.filter(user_id=userId).exists():
        return True
    else:
        return False
    
def admin_required():
    def decorator(view):
        @wraps(view)
        def _wrapped_view(request, *args, **kwargs):
            if not isAdmin(request.session.get('uid')):
                messages.error(request, 'Permission Denied')
                return JsonResponse({'status': 403, 'message': '僅管理員可訪問'}, status=403)
            return view(request, *args, **kwargs)
        return _wrapped_view
    return decorator