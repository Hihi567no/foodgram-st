"""Recipe models with enhanced functionality and custom managers."""
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

from foodgram_backend.constants import (
    MIN_COOKING_TIME, MAX_COOKING_TIME,
    MIN_INGREDIENT_AMOUNT, MAX_INGREDIENT_AMOUNT,
    MAX_RECIPE_NAME_LENGTH, MAX_INGREDIENT_NAME_LENGTH, MAX_MEASUREMENT_UNIT_LENGTH
)

User = get_user_model()


class IngredientQuerySet(models.QuerySet):
    """Custom QuerySet for Ingredient model."""

    def search_by_name(self, name):
        """Search ingredients by name (case-insensitive)."""
        return self.filter(name__icontains=name)

    def by_measurement_unit(self, unit):
        """Filter ingredients by measurement unit."""
        return self.filter(measurement_unit=unit)


class IngredientManager(models.Manager):
    """Custom manager for Ingredient model."""

    def get_queryset(self):
        """Return custom queryset."""
        return IngredientQuerySet(self.model, using=self._db)

    def search_by_name(self, name):
        """Search ingredients by name."""
        return self.get_queryset().search_by_name(name)

    def by_measurement_unit(self, unit):
        """Filter by measurement unit."""
        return self.get_queryset().by_measurement_unit(unit)


class Ingredient(models.Model):
    """Model for recipe ingredients with enhanced search capabilities."""

    name = models.CharField(
        max_length=MAX_INGREDIENT_NAME_LENGTH,
        verbose_name='Ingredient name',
        help_text='Name of the ingredient'
    )
    measurement_unit = models.CharField(
        max_length=MAX_MEASUREMENT_UNIT_LENGTH,
        verbose_name='Measurement unit',
        help_text='Unit of measurement (e.g., grams, cups, pieces)'
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


class RecipeQuerySet(models.QuerySet):
    """Custom QuerySet for Recipe model with advanced filtering."""

    def published(self):
        """Return only published recipes."""
        return self.filter(is_published=True)

    def by_author(self, author):
        """Filter recipes by author."""
        return self.filter(author=author)

    def recent(self, days=30):
        """Return recently published recipes."""
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        return self.filter(publication_date__gte=cutoff_date)

    def quick_recipes(self, max_time=30):
        """Return recipes that can be prepared quickly."""
        return self.filter(cooking_time__lte=max_time)

    def popular(self):
        """Return recipes ordered by popularity (number of favorites)."""
        return self.annotate(
            favorites_count=models.Count('user_favorites')
        ).order_by('-favorites_count')

    def with_ingredients(self, ingredient_ids):
        """Filter recipes containing specific ingredients."""
        return self.filter(ingredients__in=ingredient_ids).distinct()


class RecipeManager(models.Manager):
    """Custom manager for Recipe model."""

    def get_queryset(self):
        """Return custom queryset."""
        return RecipeQuerySet(self.model, using=self._db)

    def published(self):
        """Get published recipes."""
        return self.get_queryset().published()

    def by_author(self, author):
        """Get recipes by author."""
        return self.get_queryset().by_author(author)

    def recent(self, days=30):
        """Get recent recipes."""
        return self.get_queryset().recent(days)

    def quick_recipes(self, max_time=30):
        """Get quick recipes."""
        return self.get_queryset().quick_recipes(max_time)

    def popular(self):
        """Get popular recipes."""
        return self.get_queryset().popular()


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
        help_text='Name of the recipe'
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
        help_text='Time required to prepare the recipe in minutes'
    )
    publication_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Publication date'
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name='Is published',
        help_text='Whether this recipe is visible to other users'
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
            models.Index(fields=['is_published']),
        ]

    def __str__(self):
        """String representation of the recipe."""
        return self.name

    @property
    def total_favorites(self):
        """Return the total number of users who favorited this recipe."""
        return self.user_favorites.count()

    @property
    def is_quick_recipe(self):
        """Check if this is a quick recipe (30 minutes or less)."""
        return self.cooking_time <= 30


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
        help_text='Amount of ingredient needed'
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


class UserFavoriteRecipe(models.Model):
    """Model for user's favorite recipes."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='User'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='user_favorites',
        verbose_name='Recipe'
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Added to favorites'
    )

    class Meta:
        """Meta options for UserFavoriteRecipe model."""
        verbose_name = 'Favorite recipe'
        verbose_name_plural = 'Favorite recipes'
        ordering = ['-added_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_favorite_recipe'
            )
        ]
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['recipe']),
            models.Index(fields=['added_at']),
        ]

    def __str__(self):
        """String representation of the favorite recipe."""
        return f'{self.user.username} favorited "{self.recipe.name}"'


class UserShoppingCart(models.Model):
    """Model for user's shopping cart (recipes to buy ingredients for)."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart_items',
        verbose_name='User'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='in_shopping_carts',
        verbose_name='Recipe'
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Added to cart'
    )

    class Meta:
        """Meta options for UserShoppingCart model."""
        verbose_name = 'Shopping cart item'
        verbose_name_plural = 'Shopping cart items'
        ordering = ['-added_at']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_shopping_cart_recipe'
            )
        ]
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['recipe']),
            models.Index(fields=['added_at']),
        ]

    def __str__(self):
        """String representation of the shopping cart item."""
        return f'{self.user.username} added "{self.recipe.name}" to cart'
