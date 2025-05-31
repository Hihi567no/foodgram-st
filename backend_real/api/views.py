"""API views for the Foodgram application."""
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from djoser import views as djoser_views
from rest_framework.permissions import IsAuthenticated, AllowAny

from users.models import User, UserSubscription
from recipes.models import (
    Ingredient, Recipe, UserFavoriteRecipe, UserShoppingCart, RecipeIngredient
)
from .filters import RecipeFilterSet, IngredientFilterSet, UserFilterSet
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    IngredientSerializer, RecipeSerializer, RecipeCreateUpdateSerializer,
    RecipeMinifiedSerializer, UserAvatarSerializer,
    UserSubscriptionListSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for API results."""

    page_size_query_param = 'limit'
    page_size = 6
    max_page_size = 100


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
        'recipe_ingredients__ingredient', 'user_favorites', 'in_shopping_carts'
    ).filter(is_published=True).order_by('-publication_date')

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
        """Set the author when creating a recipe."""
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        """Add or remove recipe from user's favorites."""
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            favorite, created = UserFavoriteRecipe.objects.get_or_create(
                user=user, recipe=recipe
            )
            if created:
                serializer = RecipeMinifiedSerializer(
                    recipe, context={'request': request})
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'detail': 'Recipe already in favorites'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        elif request.method == 'DELETE':
            try:
                favorite = UserFavoriteRecipe.objects.get(
                    user=user, recipe=recipe)
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except UserFavoriteRecipe.DoesNotExist:
                return Response(
                    {'detail': 'Recipe not in favorites'},
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        """Add or remove recipe from user's shopping cart."""
        recipe = self.get_object()
        user = request.user

        if request.method == 'POST':
            cart_item, created = UserShoppingCart.objects.get_or_create(
                user=user, recipe=recipe
            )
            if created:
                serializer = RecipeMinifiedSerializer(
                    recipe, context={'request': request})
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'detail': 'Recipe already in shopping cart'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        elif request.method == 'DELETE':
            try:
                cart_item = UserShoppingCart.objects.get(
                    user=user, recipe=recipe)
                cart_item.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except UserShoppingCart.DoesNotExist:
                return Response(
                    {'detail': 'Recipe not in shopping cart'},
                    status=status.HTTP_400_BAD_REQUEST
                )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """Download shopping cart as a text file."""
        user = request.user

        # Get all ingredients from recipes in shopping cart
        ingredients = RecipeIngredient.objects.filter(
            recipe__in_shopping_carts__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')

        # Generate shopping list text
        shopping_list = "Shopping List\n" + "=" * 50 + "\n\n"

        for item in ingredients:
            shopping_list += (
                f"• {item['ingredient__name']} - "
                f"{item['total_amount']} {item['ingredient__measurement_unit']}\n"
            )

        if not ingredients:
            shopping_list += "Your shopping cart is empty.\n"

        # Return as downloadable file
        response = HttpResponse(
            shopping_list, content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="shopping_list.txt"'
        return response

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[AllowAny],
        url_path='get-link'
    )
    def get_link(self, request, pk=None):
        """Get short link for recipe."""
        recipe = self.get_object()
        short_url = request.build_absolute_uri(f'/s/{recipe.id}/')
        return Response({'short-link': short_url})


class UserManagementViewSet(djoser_views.UserViewSet):
    """Enhanced user management ViewSet with subscription functionality."""

    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = UserFilterSet
    search_fields = ['username', 'email', 'first_name', 'last_name']

    def get_permissions(self):
        """Return appropriate permissions based on action."""
        if self.action == 'me':
            return [IsAuthenticated()]
        return super().get_permissions()

    @action(
        detail=False,
        methods=['put', 'patch', 'delete'],
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

        # PUT/PATCH methods
        if not request.data or 'avatar' not in request.data:
            return Response(
                {'avatar': ['This field is required.']},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = UserAvatarSerializer(
            user, data=request.data, partial=True, context={'request': request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        """Get list of user's subscriptions."""
        user = request.user
        subscriptions = UserSubscription.objects.filter(
            subscriber=user
        ).select_related('target_user')

        # Get target users
        target_users = [sub.target_user for sub in subscriptions]

        page = self.paginate_queryset(target_users)
        if page is not None:
            serializer = UserSubscriptionListSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = UserSubscriptionListSerializer(
            target_users, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        """Subscribe or unsubscribe from a user."""
        target_user = self.get_object()
        subscriber = request.user

        if request.method == 'POST':
            if subscriber == target_user:
                return Response(
                    {'detail': 'Cannot subscribe to yourself'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            subscription, created = UserSubscription.objects.get_or_create(
                subscriber=subscriber,
                target_user=target_user
            )

            if created:
                serializer = UserSubscriptionListSerializer(
                    target_user, context={'request': request}
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {'detail': 'Already subscribed'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        elif request.method == 'DELETE':
            try:
                subscription = UserSubscription.objects.get(
                    subscriber=subscriber,
                    target_user=target_user
                )
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except UserSubscription.DoesNotExist:
                return Response(
                    {'detail': 'Not subscribed'},
                    status=status.HTTP_400_BAD_REQUEST
                )


class UserSubscriptionsListView(ListAPIView):
    """View for listing user subscriptions (separate from UserViewSet)."""

    serializer_class = UserSubscriptionListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """Get list of users that current user is subscribed to."""
        user = self.request.user
        subscribed_user_ids = UserSubscription.objects.filter(
            subscriber=user
        ).values_list('target_user_id', flat=True)

        return User.objects.filter(id__in=subscribed_user_ids)


class UserSubscribeView(APIView):
    """View for subscribing/unsubscribing to users (separate from UserViewSet)."""

    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        """Subscribe to a user."""
        target_user = get_object_or_404(User, id=id)
        subscriber = request.user

        if subscriber == target_user:
            return Response(
                {'detail': 'Cannot subscribe to yourself'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription, created = UserSubscription.objects.get_or_create(
            subscriber=subscriber,
            target_user=target_user
        )

        if created:
            serializer = UserSubscriptionListSerializer(
                target_user, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {'detail': 'Already subscribed'},
                status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, id):
        """Unsubscribe from a user."""
        target_user = get_object_or_404(User, id=id)
        subscriber = request.user

        try:
            subscription = UserSubscription.objects.get(
                subscriber=subscriber,
                target_user=target_user
            )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except UserSubscription.DoesNotExist:
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
