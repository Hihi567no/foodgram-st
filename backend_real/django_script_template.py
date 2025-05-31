"""
Template for Django standalone scripts.
Copy this template when creating new Django scripts that need to access models.
"""
import os
import django

# Setup Django environment first - ALWAYS do this before importing models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram_backend.settings')
django.setup()

# Now import Django models and other Django components after setup
# from users.models import User  # noqa: E402
# from recipes.models import Recipe, Ingredient  # noqa: E402
# from django.db import models  # noqa: E402


def main():
    """Main function for your script logic."""
    print("Django environment is set up!")
    print("You can now use Django models and ORM.")
    
    # Example usage:
    # from users.models import User
    # users = User.objects.all()
    # print(f"Total users: {users.count()}")


if __name__ == "__main__":
    main()
