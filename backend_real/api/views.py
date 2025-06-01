"""API views for the Foodgram application."""
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from djoser import views as djoser_views
from rest_framework.permissions import IsAuthenticated, AllowAny

from users.models import UserSubscription
from recipes.models import (
    Ingredient, Recipe, Favorite, ShoppingCart, RecipeIngredient
)
from .filters import RecipeFilterSet, IngredientFilterSet
from .permissions import IsAuthorOrReadOnly
from .pagination import StandardResultsSetPagination
from .utils import format_shopping_list, create_shopping_list_response
from .serializers import (
    IngredientSerializer, RecipeSerializer, RecipeCreateUpdateSerializer,
    UserAvatarSerializer, UserSubscriptionListSerializer,
    FavoriteSerializer, ShoppingCartSerializer, UserSubscriptionSerializer
)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for ingredient management (read-only)."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = IngredientFilterSet
    search_fields = ['name']
    pagination_class = None  # No pagination for ingredients


class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet for recipe management with full CRUD operations."""

    queryset = Recipe.objects.select_related('author').prefetch_related(
        'recipe_ingredients__ingredient', 'favorites', 'shoppingcarts'
    ).order_by('-publication_date')

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend,
                       filters.SearchFilter, filters.OrderingFilter]
    filterset_class = RecipeFilterSet
    search_fields = ['name', 'author__username']
    ordering_fields = ['publication_date', 'name', 'cooking_time']

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        """Set the author to the current user when creating a recipe."""
        serializer.save(author=self.request.user)

    def _add_to_collection(self, request, serializer_class):
        """Helper method to add recipe to user collection (favorites/cart)."""
        recipe = self.get_object()
        serializer = serializer_class(
            data={'user': request.user.id, 'recipe': recipe.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _remove_from_collection(self, request, model_class):
        """Helper method to remove recipe from user collection (favorites/cart)."""
        recipe = self.get_object()
        deleted_count, _ = model_class.objects.filter(
            user=request.user, recipe=recipe
        ).delete()

        if deleted_count:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {'detail': 'Recipe not found in collection'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def favorite(self, request, **kwargs):
        """Add recipe to user's favorites."""
        return self._add_to_collection(request, FavoriteSerializer)

    @favorite.mapping.delete
    def remove_favorite(self, request, **kwargs):
        """Remove recipe from user's favorites."""
        return self._remove_from_collection(request, Favorite)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, **kwargs):
        """Add recipe to user's shopping cart."""
        return self._add_to_collection(request, ShoppingCartSerializer)

    @shopping_cart.mapping.delete
    def remove_shopping_cart(self, request, **kwargs):
        """Remove recipe from user's shopping cart."""
        return self._remove_from_collection(request, ShoppingCart)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Download shopping cart as a text file."""
        # Get all ingredients from recipes in shopping cart
        ingredients = RecipeIngredient.objects.filter(
            recipe__shoppingcarts__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')

        # Format and return shopping list
        shopping_list_text = format_shopping_list(ingredients)
        return create_shopping_list_response(shopping_list_text)

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[AllowAny],
        url_path='get-link'
    )
    def get_link(self, request, **kwargs):
        """Get short link for recipe."""
        recipe = self.get_object()
        short_url = request.build_absolute_uri(
            reverse('recipe_short_link', kwargs={'recipe_id': recipe.id})
        )
        return Response({'short-link': short_url})


class UserManagementViewSet(djoser_views.UserViewSet):
    """Enhanced user management ViewSet with subscription functionality."""

    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']

    def get_permissions(self):
        """Return appropriate permissions based on action."""
        if self.action == 'me':
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(
        detail=False,
        methods=['put', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request):
        """Update or delete user avatar."""
        user = request.user

        if request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete()
                user.avatar = None
                user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        # PUT method
        serializer = UserAvatarSerializer(
            user, data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """Get list of user's subscriptions."""
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Get target users directly using double underscore syntax
        target_users = User.objects.filter(
            followers__subscriber=request.user
        ).distinct()

        page = self.paginate_queryset(target_users)
        serializer = UserSubscriptionListSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def subscribe(self, request, **kwargs):
        """Subscribe to a user."""
        target_user = self.get_object()
        serializer = UserSubscriptionSerializer(
            data={'subscriber': request.user.id, 'target_user': target_user.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, **kwargs):
        """Unsubscribe from a user."""
        target_user = self.get_object()
        deleted_count, _ = UserSubscription.objects.filter(
            subscriber=request.user, target_user=target_user
        ).delete()

        if deleted_count:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {'detail': 'Not subscribed'},
                status=status.HTTP_400_BAD_REQUEST
            )





@api_view(['GET'])
@permission_classes([AllowAny])
def recipe_short_link_redirect(request, recipe_id):
    """Redirect from short URL to recipe detail page."""
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    destination_url = f"/recipes/{recipe.pk}/"
    return HttpResponseRedirect(destination_url)
