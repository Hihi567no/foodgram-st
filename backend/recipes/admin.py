from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.safestring import mark_safe
from .models import User, Subscription, Recipe, ShoppingCart, FavoriteRecipe, IngredientInRecipe, Ingredient



@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    search_fields = ("recipe__name", "ingredient__name")
    search_help_text = "Поиск по наименованию рецепта или ингредиента"
    list_display = ('recipe__name', 'ingredient__name')


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    search_fields = ("recipe__name", "user__username")
    search_help_text = "Поиск по username пользователя или названию рецепта"
    list_display = ('recipe__name', 'user__username')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    search_fields = ("recipe__name", "user__username")
    search_help_text = "Поиск по username пользователя или названию рецепта"
    list_display = ('recipe__name', 'user__username')


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'name', 
        'cooking_time', 
        'author', 
        'in_favorites', 
        'ingredients_list', 
        'image'
    )
    search_fields = ("name", "author__username")
    search_help_text = "Поиск по названию рецепта или его автору"
    readonly_fields = ("in_favorites", "ingredients_list", "image")
    list_display_links = ('id', 'name')

    @admin.display(description="В избранном")
    def in_favorites(self, recipe):
        return recipe.favorites.count()

    @admin.display(description="Ингредиенты")
    @mark_safe
    def ingredients_list(self, recipe):
        ingredients = recipe.recipe_ingredients.all().select_related('ingredient')
        items = [f"{item.ingredient.name} - {item.amount} {item.ingredient.measurement_unit}" 
                for item in ingredients]
        return f"{'<br>'.join(items)}" if items else "-"

    @admin.display(description="Изображение")
    @mark_safe
    def image(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="100" height="100" style="object-fit: cover;" />'
        return "-"


class HasRecipesFilter(admin.SimpleListFilter):
    title = 'Наличие в рецептах'
    parameter_name = 'has_recipes'
    lookups_value = (
        ('yes', 'Есть в рецептах'),
        ('no', 'Нет в рецептах'),
    )

    def lookups(self, request, model_admin):
        return self.lookups_value
    
    def queryset(self, request, ingredients):
        if self.value() == 'yes':
            return ingredients.filter(recipe_ingredients__isnull=False).distinct()
        if self.value() == 'no':
            return ingredients.filter(recipe_ingredients__isnull=True)
        return ingredients
    

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'recipes_count')
    readonly_fields = ('recipes_count',)
    list_filter = (
        'measurement_unit',
        HasRecipesFilter,
    )
    search_fields = ('name', 'measurement_unit')
    search_help_text = "Поиск по названию ингредиента или единице измерения"

    @admin.display(description="Рецептов")
    def recipes_count(self, ingredient):
        return ingredient.recipe_ingredients.count()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    search_fields = ("user__username", "author__username")
    search_help_text = "Поиск по username"
    list_display = ('user__username', 'author__username')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'id',
        'username',
        'full_name',
        'email',
        'avatar_preview',
        'recipes_count',
        'subscriptions_count',
        'subscribers_count'
    )
    list_display_links = ('id', 'username')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    search_help_text = "Поиск по username, email или ФИО"
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'avatar')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    @admin.display(description='ФИО')
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or '-'

    @admin.display(description='Аватар')
    @mark_safe
    def avatar_preview(self, obj):
        if obj.avatar:
            return f'<img src="{obj.avatar.url}" width="50" height="50" style="object-fit: cover; border-radius: 50%;" />'
        return '-'

    @admin.display(description='Рецептов', ordering='_recipes_count')
    def recipes_count(self, user):
        return user.recipes.count()

    @admin.display(description='Подписок', ordering='_subscriptions_count')
    def subscriptions_count(self, user):
        return user.authors.count()

    @admin.display(description='Подписчиков', ordering='_subscribers_count')
    def subscribers_count(self, user):
        return user.followers.count()