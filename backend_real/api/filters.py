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
        if not self.request.user.is_authenticated or not value:
            return queryset

        # Convert string values to boolean
        is_favorited = value.lower() in ('1', 'true', 'yes', 'on')

        if is_favorited:
            return queryset.filter(favorites__user=self.request.user)
        return queryset.exclude(favorites__user=self.request.user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Filter recipes that are in user's shopping cart."""
        if not self.request.user.is_authenticated or not value:
            return queryset

        # Convert string values to boolean
        is_in_cart = value.lower() in ('1', 'true', 'yes', 'on')

        if is_in_cart:
            return queryset.filter(shoppingcarts__user=self.request.user)
        return queryset.exclude(shoppingcarts__user=self.request.user)


class IngredientFilterSet(django_filters.FilterSet):
    """Filtering for Ingredient model according to requirements."""

    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='istartswith'
    )

    class Meta:
        model = Ingredient
        fields = ['name']
