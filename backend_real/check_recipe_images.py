"""
Script to check if recipes have images loaded.
"""
import os
import django

# Setup Django environment first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram_backend.settings')
django.setup()

# Now import Django models after setup
from recipes.models import Recipe  # noqa: E402


def check_recipe_images():
    """Check which recipes have images."""
    print("Checking recipe images...")
    print("=" * 50)

    recipes = Recipe.objects.all()

    if not recipes.exists():
        print("No recipes found in database.")
        return

    for recipe in recipes:
        image_status = "✅ HAS IMAGE" if recipe.image else "❌ NO IMAGE"
        image_path = recipe.image.name if recipe.image else "None"

        print(f"Recipe: {recipe.name}")
        print(f"  Author: {recipe.author.username}")
        print(f"  Image Status: {image_status}")
        print(f"  Image Path: {image_path}")
        print(f"  Cooking Time: {recipe.cooking_time} minutes")
        print("-" * 30)

    # Summary
    total_recipes = recipes.count()
    recipes_with_images = recipes.exclude(image='').count()

    print("\nSUMMARY:")
    print(f"Total recipes: {total_recipes}")
    print(f"Recipes with images: {recipes_with_images}")
    print(f"Recipes without images: {total_recipes - recipes_with_images}")

    if recipes_with_images > 0:
        print("\n✅ SUCCESS: Some recipes have images!")
    else:
        print("\n❌ WARNING: No recipes have images.")

if __name__ == "__main__":
    check_recipe_images()
