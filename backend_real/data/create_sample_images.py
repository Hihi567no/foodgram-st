"""
Script to create sample recipe images for initial data loading.
This creates simple placeholder images with recipe names.
"""
import os
from PIL import Image, ImageDraw, ImageFont
import random

def create_recipe_image(recipe_name, filename, width=800, height=600):
    """Create a simple recipe image with the recipe name."""
    # Create a new image with a random background color
    colors = [
        (255, 182, 193),  # Light pink
        (173, 216, 230),  # Light blue
        (144, 238, 144),  # Light green
        (255, 218, 185),  # Peach
        (221, 160, 221),  # Plum
        (255, 228, 181),  # Moccasin
        (255, 160, 122),  # Light salmon
    ]

    bg_color = random.choice(colors)
    image = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(image)

    # Try to use a default font, fallback to basic if not available
    try:
        font_large = ImageFont.truetype("arial.ttf", 48)
        font_small = ImageFont.truetype("arial.ttf", 24)
    except (OSError, IOError):
        try:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        except (OSError, IOError, ImportError):
            font_large = None
            font_small = None

    # Draw recipe name
    if font_large:
        # Calculate text position to center it
        bbox = draw.textbbox((0, 0), recipe_name, font=font_large)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2 - 50

        # Draw text with shadow
        draw.text((x + 2, y + 2), recipe_name, fill=(0, 0, 0, 128), font=font_large)
        draw.text((x, y), recipe_name, fill=(255, 255, 255), font=font_large)

        # Draw "Sample Recipe" subtitle
        subtitle = "Sample Recipe"
        if font_small:
            bbox = draw.textbbox((0, 0), subtitle, font=font_small)
            subtitle_width = bbox[2] - bbox[0]
            subtitle_x = (width - subtitle_width) // 2
            subtitle_y = y + text_height + 20

            draw.text((subtitle_x + 1, subtitle_y + 1), subtitle, fill=(0, 0, 0, 128), font=font_small)
            draw.text((subtitle_x, subtitle_y), subtitle, fill=(255, 255, 255), font=font_small)

    # Add some decorative elements
    # Draw some circles to make it look more interesting
    for _ in range(5):
        x = random.randint(0, width)
        y = random.randint(0, height)
        radius = random.randint(20, 80)
        circle_color = tuple(max(0, c - 30) for c in bg_color)
        draw.ellipse([x - radius, y - radius, x + radius, y + radius],
                    fill=circle_color + (50,))

    return image

def main():
    """Create sample images for all recipes."""
    # Recipe data matching the load_initial_data.py
    recipes = [
        ("Admin Special Recipe", "admin_special.jpg"),
        ("Classic Spaghetti Carbonara", "spaghetti_carbonara.jpg"),
        ("Chicken Caesar Salad", "chicken_caesar_salad.jpg"),
        ("Beef Stir Fry", "beef_stir_fry.jpg"),
        ("Chocolate Chip Cookies", "chocolate_chip_cookies.jpg"),
    ]

    # Create the sample_images directory if it doesn't exist
    script_dir = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(script_dir, 'sample_images')
    os.makedirs(images_dir, exist_ok=True)

    print("Creating sample recipe images...")

    for recipe_name, filename in recipes:
        image_path = os.path.join(images_dir, filename)

        # Skip if image already exists
        if os.path.exists(image_path):
            print(f"Image already exists: {filename}")
            continue

        try:
            image = create_recipe_image(recipe_name, filename)
            image.save(image_path, 'JPEG', quality=85)
            print(f"Created: {filename}")
        except Exception as e:
            print(f"Error creating {filename}: {e}")

    print("Sample image creation completed!")

if __name__ == "__main__":
    main()
