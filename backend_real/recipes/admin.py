"""Admin configuration for recipe management."""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count

from .models import (
    Ingredient, Recipe, RecipeIngredient,
    Favorite, ShoppingCart
)


class RecipeIngredientInline(admin.TabularInline):
    """Inline admin for recipe ingredients."""

    model = RecipeIngredient
    extra = 1
    min_num = 1
    fields = ('ingredient', 'amount')
    autocomplete_fields = ['ingredient']


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Admin interface for Ingredient model."""

    list_display = ('name', 'measurement_unit', 'recipe_count')
    list_filter = ('measurement_unit',)
    search_fields = ('name',)
    ordering = ('name',)

    def get_queryset(self, request):
        """Optimize queryset with recipe count annotation."""
        return super().get_queryset(request).annotate(
            recipe_count=Count('recipes', distinct=True)
        )

    @admin.display(description='Used in recipes', ordering='recipe_count')
    def recipe_count(self, obj):
        """Display number of recipes using this ingredient."""
        return obj.recipe_count


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Enhanced admin interface for Recipe model."""

    list_display = (
        'name', 'author', 'cooking_time',
        'publication_date', 'favorites_count', 'image_preview'
    )
    list_filter = (
        'publication_date', 'cooking_time', 'author'
    )
    search_fields = ('name', 'author__username', 'author__email')
    ordering = ('-publication_date',)
    readonly_fields = ('publication_date', 'favorites_count', 'image_preview')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'author', 'image', 'image_preview')
        }),
        ('Recipe Details', {
            'fields': ('text', 'cooking_time')
        }),
        ('Metadata', {
            'fields': ('publication_date', 'favorites_count'),
            'classes': ('collapse',)
        }),
    )

    inlines = [RecipeIngredientInline]

    def get_queryset(self, request):
        """Optimize queryset with favorites count."""
        return super().get_queryset(request).annotate(
            favorites_count=Count('favorited_by', distinct=True)
        ).select_related('author')

    @admin.display(description='Favorites', ordering='favorites_count')
    def favorites_count(self, obj):
        """Display number of users who favorited this recipe."""
        return format_html('<strong>{}</strong>', obj.favorites_count)

    @admin.display(description='Image Preview')
    def image_preview(self, obj):
        """Display a small preview of the recipe image."""
        return format_html(
            '<img src="{}" style="width: 100px; height: 100px; object - fit: cover;" />',
            obj.image.url
        )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Admin interface for Favorite model."""

    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user', 'recipe')

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Admin interface for ShoppingCart model."""

    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user', 'recipe')

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('user', 'recipe')
