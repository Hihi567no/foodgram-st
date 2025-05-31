"""Configuration for the recipes application."""
from django.apps import AppConfig


class RecipesConfig(AppConfig):
    """Configuration class for the recipes app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'recipes'
    verbose_name = 'Recipe Management'
