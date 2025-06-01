"""
Abstract models for recipe-related functionality.
"""
from django.db import models
from django.conf import settings


class UserRecipeRelation(models.Model):
    """
    Abstract base model for user-recipe relationships.
    
    This model provides a common structure for models that represent
    a relationship between a user and a recipe (like favorites, shopping cart).
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='User'
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        verbose_name='Recipe'
    )
    
    class Meta:
        abstract = True
        # Default related_name pattern for all relation models
        default_related_name = '%(class)ss'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='%(app_label)s_%(class)s_unique_user_recipe'
            )
        ]
        indexes = [
            models.Index(fields=['user', 'recipe']),
        ]
    
    def __str__(self):
        """String representation of the relation."""
        return f'{self.user} - {self.recipe}'
