"""Tests for the recipes application."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from recipes.models import Ingredient, Recipe, RecipeIngredient

User = get_user_model()


class IngredientModelTestCase(TestCase):
    """Test cases for Ingredient model."""

    def test_ingredient_creation(self):
        """Test creating an ingredient."""
        ingredient = Ingredient.objects.create(
            name='Tomato',
            measurement_unit='g'
        )
        self.assertEqual(ingredient.name, 'Tomato')
        self.assertEqual(ingredient.measurement_unit, 'g')
        self.assertEqual(str(ingredient), 'Tomato')

    def test_ingredient_unique_name(self):
        """Test that ingredient names are unique."""
        Ingredient.objects.create(name='Tomato', measurement_unit='g')
        with self.assertRaises(Exception):
            Ingredient.objects.create(name='Tomato', measurement_unit='kg')


class RecipeModelTestCase(TestCase):
    """Test cases for Recipe model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        self.ingredient = Ingredient.objects.create(
            name='Tomato',
            measurement_unit='g'
        )

    def test_recipe_creation(self):
        """Test creating a recipe."""
        # Create a simple test image
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'fake image content',
            content_type='image/jpeg'
        )

        recipe = Recipe.objects.create(
            name='Test Recipe',
            text='Test recipe description',
            cooking_time=30,
            author=self.user,
            image=image
        )

        self.assertEqual(recipe.name, 'Test Recipe')
        self.assertEqual(recipe.text, 'Test recipe description')
        self.assertEqual(recipe.cooking_time, 30)
        self.assertEqual(recipe.author, self.user)
        self.assertEqual(str(recipe), 'Test Recipe')

    def test_recipe_ingredient_relationship(self):
        """Test recipe-ingredient relationship."""
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'fake image content',
            content_type='image/jpeg'
        )

        recipe = Recipe.objects.create(
            name='Test Recipe',
            text='Test recipe description',
            cooking_time=30,
            author=self.user,
            image=image
        )

        recipe_ingredient = RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=self.ingredient,
            amount=100
        )

        self.assertEqual(recipe_ingredient.recipe, recipe)
        self.assertEqual(recipe_ingredient.ingredient, self.ingredient)
        self.assertEqual(recipe_ingredient.amount, 100)
