from django.urls import path, include
from rest_framework import routers
from . import views


ingredients_router = routers.DefaultRouter()
ingredients_router.register("ingredients", views.IngredientViewSet, "ingredients")


urlpatterns = [path("", include(ingredients_router.urls))]
