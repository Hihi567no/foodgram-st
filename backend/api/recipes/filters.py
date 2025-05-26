from django_filters.rest_framework import CharFilter, FilterSet, BooleanFilter
from recipes.models import Recipe


class RecipeFilterSet(FilterSet):
    name = CharFilter(lookup_expr="istartswith")

    is_favorited = BooleanFilter(
        method="is_favorite_filter", field_name="favorites__user"
    )
    is_in_shopping_cart = BooleanFilter(
        method="is_in_shopping_cart_filter", field_name="shopping_carts__user"
    )

    class Meta:
        model = Recipe
        fields = ("author", "is_favorited", "is_in_shopping_cart")

    def is_favorite_filter(self, recipes, name, value):
        return self.filter_from_kwargs(recipes, value, name)

    def is_in_shopping_cart_filter(self, recipes, name, value):
        return self.filter_from_kwargs(recipes, value, name)

    def filter_from_kwargs(self, recipes, value, name):
        if value and self.request.user.id:
            return recipes.filter(**{name: self.request.user})
        return recipes
