"""URL configuration for the API application."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    IngredientViewSet, RecipeViewSet, UserManagementViewSet
)

app_name = 'api'

# Create router and register viewsets
router = DefaultRouter()

router.register('users', UserManagementViewSet, basename='user')
router.register('recipes', RecipeViewSet, basename='recipe')
router.register('ingredients', IngredientViewSet, basename='ingredient')

# Define URL patterns
urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),

    # Authentication URLs (provided by djoser)
    path('auth/', include('djoser.urls.authtoken')),
]
