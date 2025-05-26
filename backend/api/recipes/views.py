from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from io import BytesIO
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import RecipeSerializer
from recipes.models import Recipe, ShoppingCart, FavoriteRecipe
from .permissions import IsOwnerOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from recipes.pdf import ShoppingCartDocument
from .filters import RecipeFilterSet
from api.users.serializers import ShortRecipeSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ["author"]
    serializer_class = RecipeSerializer
    filterset_class = RecipeFilterSet

    def remove_entry_from_user_recipe_table(self, model, user, recipe_pk):
        get_object_or_404(
            model,
            user=user,
            recipe__pk=recipe_pk,
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def add_entry_to_user_recipe_table(self, model, user, recipe_pk, err_400_detail):
        recipe = get_object_or_404(Recipe, pk=recipe_pk)
        _, created = model.objects.get_or_create(recipe=recipe, user=user)
        if not created:
            return Response(
                {
                    "detail": err_400_detail,
                    "recipe": ShortRecipeSerializer(recipe).data
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(ShortRecipeSerializer(recipe).data, status=status.HTTP_201_CREATED)
    
    @action(
        permission_classes=[IsAuthenticated],
        methods=["post"],
        detail=True,
        url_path="favorite",
        url_name="favorite",
    )
    def favorite(self, request, pk):
        return self.add_entry_to_user_recipe_table(
            FavoriteRecipe,
            request.user,
            pk,
            "Рецепт уже добавлен в избранное"
        )

    @favorite.mapping.delete
    def delete_favorite_pair(self, request, pk=None):
        return self.remove_entry_from_user_recipe_table(
            FavoriteRecipe,
            request.user,
            pk
        )

    @action(
        permission_classes=[IsAuthenticated],
        methods=["post"],
        detail=True,
        url_path="shopping_cart",
        url_name="shopping_cart",
    )
    def shopping_cart(self, request, pk):
        return self.add_entry_to_user_recipe_table(
            ShoppingCart,
            request.user,
            pk,
            "Рецепт уже добавлен в корзину"
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        return self.remove_entry_from_user_recipe_table(
            ShoppingCart,
            request.user,
            pk
        )

    @action(
        permission_classes=[IsAuthenticated],
        methods=["get"],
        detail=False,
        url_path="download_shopping_cart",
        url_name="download_shopping_cart",
    )
    def download_shopping_cart(self, request):
        recipes = [
            item.recipe for item in self.request.user.shopping_carts.all()
        ]
        serializer = RecipeSerializer(recipes, many=True, context={"request": request})
        doc = ShoppingCartDocument(serializer.data)
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return FileResponse(
            buffer,
            as_attachment=True,
            filename="foodgram_shopping_list.pdf",
        )

    @action(
        methods=["get"],
        detail=True,
        url_path="get-link",
        url_name="get-link",
    )
    def get_link(self, request, pk):
        return Response(
            {
                "short-link": request.build_absolute_uri(
                    reverse("recipes:short_link", kwargs={"id": pk})
                )
            }
        )
