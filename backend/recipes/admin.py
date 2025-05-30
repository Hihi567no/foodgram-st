""" Админка для приложения recipes. """
from django.contrib import admin
from .models import (Favorite, Ingredient, IngredientInRecipe,
                     Recipe, ShoppingCart)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """ Админка для рецептов. """
    
    list_display = ('id', 'name', 'author', 'favorites_count')
    search_fields = ('name', 'author__username')
    list_filter = ('author', 'name')

    def favorites_count(self, obj):
        return obj.favorites.count()
    favorites_count.short_description = 'Добавлений в избранное'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка для ингредиентов."""
    
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    """Админка для связи ингредиента и рецепта."""
    
    list_display = ('id', 'recipe', 'ingredient', 'amount')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админка для пользователей."""
    
    list_display = ('id', 'user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админка для корзины."""
    
    list_display = ('id', 'user', 'recipe')
