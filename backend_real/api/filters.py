"""Custom filters for API endpoints."""
import django_filters

from recipes.models import Recipe, Ingredient
from users.models import User


class RecipeFilterSet(django_filters.FilterSet):
    """Advanced filtering for Recipe model."""

    author = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        field_name='author',
        to_field_name='id'
    )

    is_favorited = django_filters.BooleanFilter(
        method='filter_is_favorited',
        label='Is in favorites'
    )

    is_in_shopping_cart = django_filters.BooleanFilter(
        method='filter_is_in_shopping_cart',
        label='Is in shopping cart'
    )

    cooking_time_min = django_filters.NumberFilter(
        field_name='cooking_time',
        lookup_expr='gte',
        label='Minimum cooking time'
    )

    cooking_time_max = django_filters.NumberFilter(
        field_name='cooking_time',
        lookup_expr='lte',
        label='Maximum cooking time'
    )

    ingredients = django_filters.ModelMultipleChoiceFilter(
        queryset=Ingredient.objects.all(),
        field_name='ingredients',
        to_field_name='id',
        label='Contains ingredients'
    )

    is_favorited = django_filters.CharFilter(
        method='filter_is_favorited',
        label='Is in favorites'
    )

    is_in_shopping_cart = django_filters.CharFilter(
        method='filter_is_in_shopping_cart',
        label='Is in shopping cart'
    )

    class Meta:
        model = Recipe
        fields = [
            'author', 'is_favorited', 'is_in_shopping_cart',
            'cooking_time_min', 'cooking_time_max', 'ingredients'
        ]

    def filter_is_favorited(self, queryset, name, value):
        """Filter recipes that are in user's favorites."""
        if not self.request.user.is_authenticated:
            return queryset.none() if self._is_truthy(value) else queryset

        if self._is_truthy(value):
            return queryset.filter(user_favorites__user=self.request.user).distinct()
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Filter recipes that are in user's shopping cart."""
        if not self.request.user.is_authenticated:
            return queryset.none() if self._is_truthy(value) else queryset

        if self._is_truthy(value):
            return queryset.filter(in_shopping_carts__user=self.request.user).distinct()
        return queryset

    def _is_truthy(self, value):
        """Convert string values to boolean."""
        if isinstance(value, str):
            return value.lower() in ('1', 'true', 'yes', 'on')
        return bool(value)


class IngredientFilterSet(django_filters.FilterSet):
    """Filtering for Ingredient model."""

    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        label='Name contains'
    )

    name_startswith = django_filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith',
        label='Name starts with'
    )

    measurement_unit = django_filters.CharFilter(
        field_name='measurement_unit',
        lookup_expr='iexact',
        label='Measurement unit'
    )

    class Meta:
        model = Ingredient
        fields = ['name', 'name_startswith', 'measurement_unit']


class UserFilterSet(django_filters.FilterSet):
    """Filtering for User model."""

    username = django_filters.CharFilter(
        field_name='username',
        lookup_expr='icontains',
        label='Username contains'
    )

    email = django_filters.CharFilter(
        field_name='email',
        lookup_expr='icontains',
        label='Email contains'
    )

    first_name = django_filters.CharFilter(
        field_name='first_name',
        lookup_expr='icontains',
        label='First name contains'
    )

    last_name = django_filters.CharFilter(
        field_name='last_name',
        lookup_expr='icontains',
        label='Last name contains'
    )

    has_recipes = django_filters.BooleanFilter(
        method='filter_has_recipes',
        label='Has created recipes'
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name',
                  'last_name', 'has_recipes']

    def filter_has_recipes(self, queryset, name, value):
        """Filter users who have created recipes."""
        if value:
            return queryset.filter(recipes__isnull=False).distinct()
        else:
            return queryset.filter(recipes__isnull=True)
