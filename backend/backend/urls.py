"""
URL configuration for backEnd project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from cafeInfo import views as cafe_views
from user import views as user_views
from django.conf.urls.static import static
from django.conf import settings
from mail import views as mail_views

urlpatterns = [
    path("signup/", user_views.sign_up),
    path("login/", user_views.login_view),
    path("user/", user_views.get_information),
    path("admin/", admin.site.urls),
    path("cafes/", cafe_views.get_all_cafes, name="get_all_cafes"),
    path("cafe/", cafe_views.get_cafe, name="get_cafe"),
    path(
        "cafes/filter/",
        cafe_views.filter_cafes_by_labels,
        name="filter_cafes_by_labels",
    ),
    path(
        "cafes/top/",
        cafe_views.get_top_cafes,
        name="get_top_cafes",
    ),
    path("metro-stations/", cafe_views.get_all_metro_stations),
    path("user/email/", mail_views.send_email_view),
    path("user/check/<str:token>", user_views.check),
    path("pw/forgot/", mail_views.forgot),
    path("pw/reset/", user_views.reset_password),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
