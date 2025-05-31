"""Tests for the API application."""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from recipes.models import Ingredient

User = get_user_model()


class APITestCase(APITestCase):
    """Base test case for API tests."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        self.ingredient = Ingredient.objects.create(
            name='Test Ingredient',
            measurement_unit='g'
        )

    def test_ingredients_list(self):
        """Test ingredients list endpoint."""
        url = reverse('api:ingredient-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Ingredient')

    def test_users_list(self):
        """Test users list endpoint."""
        url = reverse('api:user-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class ModelTestCase(TestCase):
    """Test cases for models."""

    def test_user_creation(self):
        """Test user model creation."""
        user = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            first_name='Test2',
            last_name='User2'
        )
        self.assertEqual(user.username, 'testuser2')
        self.assertEqual(user.email, 'test2@example.com')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)

    def test_ingredient_creation(self):
        """Test ingredient model creation."""
        ingredient = Ingredient.objects.create(
            name='Test Ingredient 2',
            measurement_unit='ml'
        )
        self.assertEqual(ingredient.name, 'Test Ingredient 2')
        self.assertEqual(ingredient.measurement_unit, 'ml')
        self.assertEqual(str(ingredient), 'Test Ingredient 2')
