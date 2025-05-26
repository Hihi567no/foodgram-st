from django.urls import path, include
from rest_framework import routers
from . import views

app_name = "users"

user_router = routers.DefaultRouter()
user_router.register("users", views.FoodgramUserViewSet, "users")


urlpatterns = [path("", include(user_router.urls))]
