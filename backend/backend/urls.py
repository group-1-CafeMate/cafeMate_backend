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

urlpatterns = [
    path("admin/", admin.site.urls),
    path("cafes/", cafe_views.get_all_cafes, name="get_all_cafes"),
    path("cafe/", cafe_views.get_cafe, name="get_cafe"),
    path(
        "cafes/filter/",
        cafe_views.filter_cafes_by_labels,
        name="filter_cafes_by_labels",
    ),
]
