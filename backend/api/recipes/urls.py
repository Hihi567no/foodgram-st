from django.urls import path, include
from rest_framework import routers
from . import views

recipes_router = routers.DefaultRouter()
recipes_router.register("recipes", views.RecipeViewSet, "recipes")


urlpatterns = [
    path("", include(recipes_router.urls)),
]
