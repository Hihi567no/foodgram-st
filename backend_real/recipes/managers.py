"""
Custom managers for recipe models.
"""
from django.db import models

from .querysets import IngredientQuerySet, RecipeQuerySet


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
