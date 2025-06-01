#!/usr/bin/env python
"""
Script to set up test data for Postman tests.
Run this script to ensure all required test data exists.
"""
import os
import sys
import django
from django.core.files.base import ContentFile
import base64

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram_backend.settings')
django.setup()

# Django imports must come after django.setup() - ruff: disable=E402
from django.contrib.auth import get_user_model  # noqa: E402
from recipes.models import Ingredient, Recipe, RecipeIngredient, Favorite, ShoppingCart  # noqa: E402

User = get_user_model()

def create_test_users():
    """Create test users with specific IDs."""
    print("Creating test users...")

    users_data = [
        (5, 'testuser5', 'testuser5@example.com', 'Test', 'User5'),
        (6, 'testuser6', 'testuser6@example.com', 'Second', 'User'),
        (7, 'testuser7', 'testuser7@example.com', 'Third', 'User'),
    ]

    created_users = []
    for user_id, username, email, first_name, last_name in users_data:
        user, created = User.objects.get_or_create(
            id=user_id,
            defaults={
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'password': 'pbkdf2_sha256$600000$test$hash'  # Dummy hash
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
            print(f"Created user: {user.username} (ID: {user.id})")
        else:
            print(f"User already exists: {user.username} (ID: {user.id})")

        created_users.append(user)

    return created_users

def create_test_ingredients():
    """Create test ingredients including ones starting with 'S'."""
    print("Creating test ingredients...")
    
    ingredients_data = [
        ('Salt', 'g'),
        ('Sugar', 'g'),
        ('Soy sauce', 'ml'),
        ('Spinach', 'g'),
        ('Salmon', 'g'),
        ('Flour', 'g'),
        ('Milk', 'ml'),
        ('Butter', 'g'),
        ('Eggs', 'pcs'),
        ('Tomato', 'pcs'),
    ]
    
    created_ingredients = []
    for name, unit in ingredients_data:
        ingredient, created = Ingredient.objects.get_or_create(
            name=name,
            defaults={'measurement_unit': unit}
        )
        created_ingredients.append(ingredient)
        if created:
            print(f"Created ingredient: {ingredient.name}")
        else:
            print(f"Ingredient already exists: {ingredient.name}")
    
    return created_ingredients

def create_test_recipes(users, ingredients):
    """Create test recipes for multiple users."""
    print("Creating test recipes...")

    # Create a simple 1x1 pixel PNG image
    image_data = base64.b64decode(
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
    )

    recipes_data = [
        {
            'name': 'Test Recipe 1',
            'text': 'This is a test recipe for Postman tests.',
            'cooking_time': 30,
            'author_index': 0,  # First user
        },
        {
            'name': 'Test Recipe 2',
            'text': 'Another test recipe for comprehensive testing.',
            'cooking_time': 45,
            'author_index': 1,  # Second user
        },
        {
            'name': 'Quick Recipe',
            'text': 'A quick recipe for testing.',
            'cooking_time': 15,
            'author_index': 0,  # First user
        },
        {
            'name': 'User 2 Special Recipe',
            'text': 'Special recipe by second user.',
            'cooking_time': 60,
            'author_index': 1,  # Second user
        },
        {
            'name': 'User 3 Delicious Recipe',
            'text': 'Delicious recipe by third user.',
            'cooking_time': 25,
            'author_index': 2,  # Third user
        }
    ]

    created_recipes = []
    for i, recipe_data in enumerate(recipes_data):
        author = users[recipe_data['author_index']]
        recipe, created = Recipe.objects.get_or_create(
            name=recipe_data['name'],
            author=author,
            defaults={
                'text': recipe_data['text'],
                'cooking_time': recipe_data['cooking_time'],
                'image': ContentFile(image_data, name=f'test_recipe_{i+1}.png')
            }
        )

        if created:
            # Add ingredients to recipe
            recipe_ingredients = []
            for j, ingredient in enumerate(ingredients[:3]):  # Use first 3 ingredients
                recipe_ingredient = RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=100 + (j * 50)  # 100, 150, 200
                )
                recipe_ingredients.append(recipe_ingredient)

            RecipeIngredient.objects.bulk_create(recipe_ingredients)
            print(f"Created recipe: {recipe.name} by {author.username} with {len(recipe_ingredients)} ingredients")
        else:
            print(f"Recipe already exists: {recipe.name}")

        created_recipes.append(recipe)

    return created_recipes

def create_favorites_and_shopping_cart(users, recipes):
    """Create some favorites and shopping cart entries for testing filters."""
    print("Creating favorites and shopping cart entries...")

    # Add first recipe to favorites for first user (testuser5)
    favorite, created = Favorite.objects.get_or_create(
        user=users[0],  # testuser5
        recipe=recipes[0]  # First recipe
    )
    if created:
        print(f"Added {recipes[0].name} to favorites for {users[0].username}")

    # Add second recipe to favorites for first user
    favorite, created = Favorite.objects.get_or_create(
        user=users[0],  # testuser5
        recipe=recipes[1]  # Second recipe
    )
    if created:
        print(f"Added {recipes[1].name} to favorites for {users[0].username}")

    # Add first recipe to shopping cart for first user
    cart_item, created = ShoppingCart.objects.get_or_create(
        user=users[0],  # testuser5
        recipe=recipes[0]  # First recipe
    )
    if created:
        print(f"Added {recipes[0].name} to shopping cart for {users[0].username}")

    # Add third recipe to shopping cart for first user
    cart_item, created = ShoppingCart.objects.get_or_create(
        user=users[0],  # testuser5
        recipe=recipes[2]  # Third recipe
    )
    if created:
        print(f"Added {recipes[2].name} to shopping cart for {users[0].username}")

def main():
    """Main function to set up all test data."""
    print("Setting up test data for Postman tests...")
    print("=" * 50)
    
    try:
        # Create test users
        users = create_test_users()

        # Create test ingredients
        ingredients = create_test_ingredients()

        # Create test recipes
        recipes = create_test_recipes(users, ingredients)

        # Create favorites and shopping cart entries
        create_favorites_and_shopping_cart(users, recipes)

        print("=" * 50)
        print("Test data setup completed successfully!")
        print("Created/verified:")
        print(f"- {len(users)} test users")
        for user in users:
            print(f"  - {user.username} (ID: {user.id})")
        print(f"- {len(ingredients)} ingredients")
        print(f"- {len(recipes)} recipes")
        print("- Favorites and shopping cart entries for testing filters")
        print("\nIngredients starting with 'S':")
        s_ingredients = [ing for ing in ingredients if ing.name.startswith('S')]
        for ing in s_ingredients:
            print(f"  - {ing.name} ({ing.measurement_unit})")

    except Exception as e:
        print(f"Error setting up test data: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
