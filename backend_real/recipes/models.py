"""Recipe models with enhanced functionality."""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

from foodgram_backend.constants import (
    MIN_COOKING_TIME, MAX_COOKING_TIME,
    MIN_INGREDIENT_AMOUNT, MAX_INGREDIENT_AMOUNT,
    MAX_RECIPE_NAME_LENGTH, MAX_INGREDIENT_NAME_LENGTH, MAX_MEASUREMENT_UNIT_LENGTH,
    QUICK_RECIPE_TIME_LIMIT
)
from .managers import IngredientManager, RecipeManager
from .abstract_models import UserRecipeRelation

User = get_user_model()





class Ingredient(models.Model):
    """Model for recipe ingredients with enhanced search capabilities."""

    name = models.CharField(
        max_length=MAX_INGREDIENT_NAME_LENGTH,
        verbose_name='Ingredient name',
        help_text=f'Name of the ingredient (max {MAX_INGREDIENT_NAME_LENGTH} characters)'
    )
    measurement_unit = models.CharField(
        max_length=MAX_MEASUREMENT_UNIT_LENGTH,
        verbose_name='Measurement unit',
        help_text=f'Unit of measurement (max {MAX_MEASUREMENT_UNIT_LENGTH} characters, e.g., grams, cups, pieces)'
    )

    objects = IngredientManager()

    class Meta:
        """Meta options for Ingredient model."""
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient_measurement'
            )
        ]
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['measurement_unit']),
        ]

    def __str__(self):
        """String representation of the ingredient."""
        return f'{self.name}, {self.measurement_unit}'





class Recipe(models.Model):
    """Enhanced recipe model with additional functionality."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Recipe author',
        help_text='User who created this recipe'
    )
    name = models.CharField(
        max_length=MAX_RECIPE_NAME_LENGTH,
        verbose_name='Recipe name',
        help_text=f'Name of the recipe (max {MAX_RECIPE_NAME_LENGTH} characters)'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Recipe image',
        help_text='Image of the prepared dish'
    )
    text = models.TextField(
        verbose_name='Recipe description',
        help_text='Detailed cooking instructions'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ingredients',
        help_text='Ingredients used in this recipe'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Cooking time (minutes)',
        validators=[
            MinValueValidator(
                MIN_COOKING_TIME,
                message=f'Cooking time must be at least {MIN_COOKING_TIME} minute'
            ),
            MaxValueValidator(
                MAX_COOKING_TIME,
                message=f'Cooking time cannot exceed {MAX_COOKING_TIME} minutes'
            )
        ],
        help_text=f'Time required to prepare the recipe in minutes ({MIN_COOKING_TIME}-{MAX_COOKING_TIME})'
    )
    publication_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Publication date'
    )

    # Many-to-many relationships through intermediate models
    favorited_by = models.ManyToManyField(
        User,
        through='Favorite',
        related_name='favorite_recipes',
        blank=True,
        verbose_name='Users who favorited this recipe'
    )
    in_shopping_carts = models.ManyToManyField(
        User,
        through='ShoppingCart',
        related_name='shopping_cart_recipes',
        blank=True,
        verbose_name='Users who added this recipe to shopping cart'
    )

    objects = RecipeManager()

    class Meta:
        """Meta options for Recipe model."""
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'
        ordering = ['-publication_date']
        indexes = [
            models.Index(fields=['author']),
            models.Index(fields=['publication_date']),
            models.Index(fields=['cooking_time']),
        ]

    def __str__(self):
        """String representation of the recipe."""
        return self.name

    @property
    def is_quick_recipe(self):
        """
        Check if this is a quick recipe.

        Returns:
            bool: True if cooking time is within the quick recipe limit.

        Note:
            The time limit is defined by QUICK_RECIPE_TIME_LIMIT constant.
        """
        return self.cooking_time <= QUICK_RECIPE_TIME_LIMIT


class RecipeIngredient(models.Model):
    """Through model for Recipe-Ingredient relationship with amounts."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Recipe'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',
        verbose_name='Ingredient'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Amount',
        validators=[
            MinValueValidator(
                MIN_INGREDIENT_AMOUNT,
                message=f'Amount must be at least {MIN_INGREDIENT_AMOUNT}'
            ),
            MaxValueValidator(
                MAX_INGREDIENT_AMOUNT,
                message=f'Amount cannot exceed {MAX_INGREDIENT_AMOUNT}'
            )
        ],
        help_text=f'Amount of ingredient needed ({MIN_INGREDIENT_AMOUNT}-{MAX_INGREDIENT_AMOUNT})'
    )

    class Meta:
        """Meta options for RecipeIngredient model."""
        verbose_name = 'Recipe ingredient'
        verbose_name_plural = 'Recipe ingredients'
        ordering = ['recipe', 'ingredient']
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient_combination'
            )
        ]
        indexes = [
            models.Index(fields=['recipe']),
            models.Index(fields=['ingredient']),
        ]

    def __str__(self):
        """String representation of the recipe ingredient."""
        return f'{self.ingredient.name} - {self.amount} {self.ingredient.measurement_unit}'


class Favorite(UserRecipeRelation):
    """Model for user's favorite recipes."""

    class Meta(UserRecipeRelation.Meta):
        """Meta options for Favorite model."""
        verbose_name = 'Favorite recipe'
        verbose_name_plural = 'Favorite recipes'


class ShoppingCart(UserRecipeRelation):
    """Model for user's shopping cart (recipes to buy ingredients for)."""

    class Meta(UserRecipeRelation.Meta):
        """Meta options for ShoppingCart model."""
        verbose_name = 'Shopping cart item'
        verbose_name_plural = 'Shopping cart items'
