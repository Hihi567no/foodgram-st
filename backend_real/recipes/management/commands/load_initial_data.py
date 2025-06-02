"""Management command to load initial data (admin user, sample users, and recipes)."""
import random
import subprocess
import sys
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Recipe, RecipeIngredient

User = get_user_model()


class Command(BaseCommand):
    """Load initial data including admin user, sample users, and recipes."""

    help = 'Load initial data for development and testing'

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--skip-admin',
            action='store_true',
            help='Skip creating admin user',
        )
        parser.add_argument(
            '--skip-users',
            action='store_true',
            help='Skip creating sample users',
        )
        parser.add_argument(
            '--skip-recipes',
            action='store_true',
            help='Skip creating sample recipes',
        )

    def handle(self, *args, **options):
        """Execute the command logic."""
        self.stdout.write(
            self.style.SUCCESS('Starting initial data loading...')
        )

        # Create sample images first
        self.create_sample_images()

        if not options['skip_admin']:
            self.create_admin_user()

        if not options['skip_users']:
            created_users = self.create_sample_users()
        else:
            created_users = []

        if not options['skip_recipes']:
            # Get all users if none were created (they already exist)
            if not created_users:
                created_users = list(User.objects.filter(
                    email__in=[
                        'john.doe@example.com',
                        'jane.smith@example.com',
                        'chef.gordon@example.com'
                    ]
                ))
            self.create_sample_recipes(created_users)

        self.stdout.write(
            self.style.SUCCESS('Initial data loading completed successfully!')
        )

    def create_sample_images(self):
        """Create sample images for recipes if they don't exist."""
        try:
            # Get the path to the create_sample_images.py script
            current_dir = Path(__file__).resolve().parent.parent.parent.parent
            script_path = current_dir / 'data' / 'create_sample_images.py'

            if script_path.exists():
                self.stdout.write('Creating sample recipe images...')
                # Run the image creation script
                result = subprocess.run([
                    sys.executable, str(script_path)
                ], capture_output=True, text=True, cwd=str(current_dir / 'data'))

                if result.returncode == 0:
                    self.stdout.write(
                        self.style.SUCCESS('Sample images created successfully!')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Image creation failed: {result.stderr}')
                    )
            else:
                self.stdout.write(
                    self.style.WARNING('Sample image creation script not found')
                )
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Could not create sample images: {e}')
            )

    def create_admin_user(self):
        """Create admin user if it doesn't exist."""
        admin_email = 'admin@foodgram.com'

        if User.objects.filter(email=admin_email).exists():
            self.stdout.write(
                self.style.WARNING('Admin user already exists')
            )
            return

        # Clear all users first to ensure consistent IDs
        User.objects.all().delete()

        admin_user = User.objects.create_superuser(
            email=admin_email,
            username='admin',
            first_name='Admin',
            last_name='User',
            password='admin123'
        )

        self.stdout.write(
            self.style.SUCCESS(f'Created admin user: {admin_user.email} with ID: {admin_user.id}')
        )

    def create_sample_users(self):
        """Create sample users for testing."""
        sample_users_data = [
            {
                'email': 'john.doe@example.com',
                'username': 'johndoe',
                'first_name': 'John',
                'last_name': 'Doe',
                'password': 'testpass123'
            },
            {
                'email': 'jane.smith@example.com',
                'username': 'janesmith',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'password': 'testpass123'
            },
            {
                'email': 'chef.gordon@example.com',
                'username': 'chefgordon',
                'first_name': 'Gordon',
                'last_name': 'Ramsay',
                'password': 'testpass123'
            },
        ]

        created_users = []

        for user_data in sample_users_data:
            if User.objects.filter(email=user_data['email']).exists():
                self.stdout.write(
                    self.style.WARNING(f'User {user_data["email"]} already exists')
                )
                continue

            user = User.objects.create_user(**user_data)
            created_users.append(user)

            self.stdout.write(
                self.style.SUCCESS(f'Created user: {user.email}')
            )

        return created_users

    def create_sample_recipes(self, users):
        """Create sample recipes for testing."""
        if not Ingredient.objects.exists():
            self.stdout.write(
                self.style.WARNING(
                    'No ingredients found. Run load_ingredients command first.'
                )
            )
            return

        sample_recipes_data = [
            {
                'name': 'Admin Special Recipe',
                'text': 'A special recipe created by the admin user for testing.',
                'cooking_time': 15,
                'author_username': 'admin',  # Assign to admin user
                'image_filename': 'admin_special.jpg',
            },
            {
                'name': 'Classic Spaghetti Carbonara',
                'text': 'A traditional Italian pasta dish with eggs, cheese, and pancetta.',
                'cooking_time': 25,
                'image_filename': 'spaghetti_carbonara.jpg',
            },
            {
                'name': 'Chicken Caesar Salad',
                'text': 'Fresh romaine lettuce with grilled chicken, croutons, and Caesar dressing.',
                'cooking_time': 15,
                'image_filename': 'chicken_caesar_salad.jpg',
            },
            {
                'name': 'Beef Stir Fry',
                'text': 'Quick and easy beef stir fry with vegetables and soy sauce.',
                'cooking_time': 20,
                'image_filename': 'beef_stir_fry.jpg',
            },
            {
                'name': 'Chocolate Chip Cookies',
                'text': 'Homemade chocolate chip cookies that are crispy on the outside and chewy inside.',
                'cooking_time': 30,
                'image_filename': 'chocolate_chip_cookies.jpg',
            },
        ]

        ingredients = list(Ingredient.objects.all()[:10])  # Get first 10 ingredients

        for recipe_data in sample_recipes_data:
            # Check if specific author is requested
            if 'author_username' in recipe_data:
                try:
                    author = User.objects.get(username=recipe_data['author_username'])
                except User.DoesNotExist:
                    author = random.choice(users)
            else:
                author = random.choice(users)

            if Recipe.objects.filter(name=recipe_data['name']).exists():
                self.stdout.write(
                    self.style.WARNING(f'Recipe "{recipe_data["name"]}" already exists')
                )
                continue

            # Prepare recipe creation data
            recipe_kwargs = {
                'author': author,
                'name': recipe_data['name'],
                'text': recipe_data['text'],
                'cooking_time': recipe_data['cooking_time'],
            }

            # Add image if available
            image_file = self.get_recipe_image(recipe_data.get('image_filename'))
            if image_file:
                recipe_kwargs['image'] = image_file

            recipe = Recipe.objects.create(**recipe_kwargs)

            # Add random ingredients to the recipe
            recipe_ingredients = random.sample(ingredients, k=random.randint(3, 6))
            for ingredient in recipe_ingredients:
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=random.randint(1, 500)
                )

            self.stdout.write(
                self.style.SUCCESS(f'Created recipe: "{recipe.name}" by {author.username}')
            )

    def get_recipe_image(self, image_filename):
        """Get a Django File object for the recipe image."""
        if not image_filename:
            return None

        try:
            # Get the path to the sample images directory
            current_dir = Path(__file__).resolve().parent.parent.parent.parent
            image_path = current_dir / 'data' / 'sample_images' / image_filename

            if image_path.exists():
                with open(image_path, 'rb') as f:
                    django_file = File(f, name=image_filename)
                    # Read the file content into memory so we can close the file
                    content = django_file.read()
                    django_file.seek(0)

                # Create a new File object with the content
                from django.core.files.base import ContentFile
                return ContentFile(content, name=image_filename)
            else:
                self.stdout.write(
                    self.style.WARNING(f'Image file not found: {image_filename}')
                )
                return None
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'Error loading image {image_filename}: {e}')
            )
            return None
