"""
Custom managers and querysets for recipe models.
"""
from django.db import models
from django.db.models import Count, Exists, OuterRef

from foodgram_backend.constants import QUICK_RECIPE_TIME_LIMIT


class IngredientQuerySet(models.QuerySet):
    """Custom QuerySet for Ingredient model."""
    
    def with_recipe_count(self):
        """Annotate ingredients with the count of recipes using them."""
        return self.annotate(
            recipe_count=Count('recipe_ingredients', distinct=True)
        )
    
    def popular(self, min_recipes=1):
        """Filter ingredients used in at least min_recipes recipes."""
        return self.with_recipe_count().filter(recipe_count__gte=min_recipes)
    
    def search_by_name(self, name):
        """Search ingredients by name (case-insensitive)."""
        return self.filter(name__icontains=name)


class IngredientManager(models.Manager):
    """Custom manager for Ingredient model."""
    
    def get_queryset(self):
        """Return custom queryset with recipe count annotation."""
        return IngredientQuerySet(self.model, using=self._db).with_recipe_count()
    
    def popular(self, min_recipes=1):
        """Get popular ingredients used in multiple recipes."""
        return self.get_queryset().popular(min_recipes)
    
    def search(self, name):
        """Search ingredients by name."""
        return self.get_queryset().search_by_name(name)


class RecipeQuerySet(models.QuerySet):
    """Custom QuerySet for Recipe model."""
    
    def with_favorites_count(self):
        """Annotate recipes with favorites count."""
        return self.annotate(
            favorites_count=Count('favorites', distinct=True)
        )
    
    def with_is_favorited(self, user):
        """Annotate recipes with is_favorited flag for specific user."""
        if user.is_anonymous:
            return self.annotate(is_favorited=models.Value(False))
        
        return self.annotate(
            is_favorited=Exists(
                self.model.favorites.through.objects.filter(
                    recipe=OuterRef('pk'),
                    user=user
                )
            )
        )
    
    def with_is_in_shopping_cart(self, user):
        """Annotate recipes with is_in_shopping_cart flag for specific user."""
        if user.is_anonymous:
            return self.annotate(is_in_shopping_cart=models.Value(False))
        
        return self.annotate(
            is_in_shopping_cart=Exists(
                self.model.shopping_cart.through.objects.filter(
                    recipe=OuterRef('pk'),
                    user=user
                )
            )
        )
    
    def quick_recipes(self):
        """Filter recipes that can be prepared quickly."""
        return self.filter(cooking_time__lte=QUICK_RECIPE_TIME_LIMIT)
    
    def by_author(self, author):
        """Filter recipes by specific author."""
        return self.filter(author=author)
    
    def by_tags(self, tags):
        """Filter recipes by tags."""
        return self.filter(tags__in=tags).distinct()
    
    def search_by_name(self, name):
        """Search recipes by name (case-insensitive)."""
        return self.filter(name__icontains=name)


class RecipeManager(models.Manager):
    """Custom manager for Recipe model."""
    
    def get_queryset(self):
        """Return custom queryset with favorites count annotation."""
        return RecipeQuerySet(self.model, using=self._db).with_favorites_count()
    
    def for_user(self, user):
        """Get recipes with user-specific annotations."""
        return (
            self.get_queryset()
            .with_is_favorited(user)
            .with_is_in_shopping_cart(user)
        )
    
    def quick_recipes(self):
        """Get recipes that can be prepared quickly."""
        return self.get_queryset().quick_recipes()
    
    def by_author(self, author):
        """Get recipes by specific author."""
        return self.get_queryset().by_author(author)
    
    def search(self, name):
        """Search recipes by name."""
        return self.get_queryset().search_by_name(name)
