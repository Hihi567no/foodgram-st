"""Application-wide constants and configuration values."""

# Recipe validation constants
MIN_COOKING_TIME = 1
MAX_COOKING_TIME = 32000
QUICK_RECIPE_TIME_LIMIT = 30  # minutes

# Ingredient amount validation constants
MIN_INGREDIENT_AMOUNT = 1
MAX_INGREDIENT_AMOUNT = 32000

# Pagination settings
DEFAULT_PAGE_SIZE = 6
MAX_PAGE_SIZE = 100

# File upload settings
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_FORMATS = ['JPEG', 'PNG', 'WEBP']

# User settings
MAX_USERNAME_LENGTH = 150
MAX_EMAIL_LENGTH = 254
MAX_NAME_LENGTH = 150

# Recipe settings
MAX_RECIPE_NAME_LENGTH = 200
MAX_INGREDIENT_NAME_LENGTH = 200
MAX_MEASUREMENT_UNIT_LENGTH = 200
