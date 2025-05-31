"""URL configuration for the API application."""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    IngredientViewSet, RecipeViewSet, UserManagementViewSet,
    UserSubscriptionsListView, UserSubscribeView
)

app_name = 'api'

# Create router and register viewsets
router = DefaultRouter()

router.register(r'users', UserManagementViewSet, basename='user')
router.register(r'recipes', RecipeViewSet, basename='recipe')
router.register(r'ingredients', IngredientViewSet, basename='ingredient')

# Custom subscription paths (to match original backend structure)
custom_user_paths = [
    path(
        'users/subscriptions/',
        UserSubscriptionsListView.as_view(),
        name='subscriptions-list'
    ),
    path(
        'users/<int:id>/subscribe/',
        UserSubscribeView.as_view(),
        name='subscribe'
    ),
]

# Define URL patterns
urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),

    # Custom subscription URLs
    path('', include(custom_user_paths)),

    # Authentication URLs (provided by djoser)
    path('auth/', include('djoser.urls.authtoken')),
]
