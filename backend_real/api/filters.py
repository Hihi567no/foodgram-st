"""Custom filters for API endpoints."""
import django_filters

from recipes.models import Recipe, Ingredient


class RecipeFilterSet(django_filters.FilterSet):
    """Filtering for Recipe model according to requirements."""

    author = django_filters.NumberFilter(field_name='author__id')
    is_favorited = django_filters.CharFilter(method='filter_is_favorited')
    is_in_shopping_cart = django_filters.CharFilter(method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['author', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        """Filter recipes that are in user's favorites."""
        if not self.request.user.is_authenticated:
            return queryset

        # Handle both boolean True and string "1" as True
        if value is True or value == "1" or value == 1:
            return queryset.filter(favorites__user=self.request.user)
        elif value is False or value == "0" or value == 0:
            return queryset.exclude(favorites__user=self.request.user)

        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Filter recipes that are in user's shopping cart."""
        if not self.request.user.is_authenticated:
            return queryset

        # Handle both boolean True and string "1" as True
        if value is True or value == "1" or value == 1:
            return queryset.filter(shoppingcarts__user=self.request.user)
        elif value is False or value == "0" or value == 0:
            return queryset.exclude(shoppingcarts__user=self.request.user)

        return queryset


class IngredientFilterSet(django_filters.FilterSet):
    """Filtering for Ingredient model according to requirements."""

    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ['name']
