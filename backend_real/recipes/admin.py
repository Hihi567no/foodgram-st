"""Admin configuration for recipe management."""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count

from .models import (
    Ingredient, Recipe, RecipeIngredient,
    UserFavoriteRecipe, UserShoppingCart
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

    def recipe_count(self, obj):
        """Display number of recipes using this ingredient."""
        return obj.recipe_count
    recipe_count.short_description = 'Used in recipes'
    recipe_count.admin_order_field = 'recipe_count'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Enhanced admin interface for Recipe model."""

    list_display = (
        'name', 'author', 'cooking_time', 'is_published',
        'publication_date', 'favorites_count', 'image_preview'
    )
    list_filter = (
        'is_published', 'publication_date', 'cooking_time', 'author'
    )
    search_fields = ('name', 'author__username', 'author__email')
    ordering = ('-publication_date',)
    readonly_fields = ('publication_date', 'favorites_count', 'image_preview')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'author', 'image', 'image_preview')
        }),
        ('Recipe Details', {
            'fields': ('text', 'cooking_time', 'is_published')
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
            favorites_count=Count('user_favorites', distinct=True)
        ).select_related('author')

    def favorites_count(self, obj):
        """Display number of users who favorited this recipe."""
        return format_html('<strong>{}</strong>', obj.favorites_count)
    favorites_count.short_description = 'Favorites'
    favorites_count.admin_order_field = 'favorites_count'

    def image_preview(self, obj):
        """Display a small preview of the recipe image."""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 100px; object-fit: cover;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Image Preview'


@admin.register(UserFavoriteRecipe)
class UserFavoriteRecipeAdmin(admin.ModelAdmin):
    """Admin interface for UserFavoriteRecipe model."""

    list_display = ('user', 'recipe', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'recipe__name')
    ordering = ('-added_at',)

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('user', 'recipe')


@admin.register(UserShoppingCart)
class UserShoppingCartAdmin(admin.ModelAdmin):
    """Admin interface for UserShoppingCart model."""

    list_display = ('user', 'recipe', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'recipe__name')
    ordering = ('-added_at',)

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('user', 'recipe')
