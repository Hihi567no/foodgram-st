"""
Database utility functions for clearing and managing data.
"""
import os
import shutil
from django.db import connection
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session
from django.contrib.admin.models import LogEntry
from rest_framework.authtoken.models import Token

from users.models import UserSubscription
from recipes.models import (
    Ingredient, Recipe, RecipeIngredient, 
    Favorite, ShoppingCart
)

User = get_user_model()


def clear_media_files():
    """
    Clear all uploaded media files.
    
    Returns:
        bool: True if successful, False otherwise
    """
    media_root = settings.MEDIA_ROOT
    if not os.path.exists(media_root):
        return True
    
    try:
        for filename in os.listdir(media_root):
            file_path = os.path.join(media_root, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        return True
    except Exception as e:
        print(f"Error clearing media files: {e}")
        return False


def clear_database_tables():
    """
    Clear all data from database tables in the correct order.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Clear in dependency order to avoid foreign key constraints
        RecipeIngredient.objects.all().delete()
        Favorite.objects.all().delete()
        ShoppingCart.objects.all().delete()
        Recipe.objects.all().delete()
        Ingredient.objects.all().delete()
        UserSubscription.objects.all().delete()
        Token.objects.all().delete()
        LogEntry.objects.all().delete()
        Session.objects.all().delete()
        User.objects.all().delete()
        ContentType.objects.all().delete()
        
        return True
    except Exception as e:
        print(f"Error clearing database tables: {e}")
        return False


def reset_auto_increment_counters():
    """
    Reset auto-increment counters for all tables (SQLite specific).
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with connection.cursor() as cursor:
            # Get all table names
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            
            # Reset auto-increment for each table
            for table in tables:
                cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}'")
        
        return True
    except Exception as e:
        print(f"Error resetting auto-increment counters: {e}")
        return False


def vacuum_database():
    """
    Vacuum the database to reclaim space.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("VACUUM")
        return True
    except Exception as e:
        print(f"Error vacuuming database: {e}")
        return False


def clear_database(include_media=True, reset_counters=True, vacuum=True):
    """
    Clear the entire database and optionally media files.
    
    Args:
        include_media (bool): Whether to clear media files
        reset_counters (bool): Whether to reset auto-increment counters
        vacuum (bool): Whether to vacuum the database
    
    Returns:
        bool: True if successful, False otherwise
    """
    success = True
    
    # Clear database tables
    if not clear_database_tables():
        success = False
    
    # Reset auto-increment counters
    if reset_counters and not reset_auto_increment_counters():
        success = False
    
    # Vacuum database
    if vacuum and not vacuum_database():
        success = False
    
    # Clear media files
    if include_media and not clear_media_files():
        success = False
    
    return success


def clear_user_data_only():
    """
    Clear only user-generated data, keep system data intact.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Clear user-generated content only
        RecipeIngredient.objects.all().delete()
        Favorite.objects.all().delete()
        ShoppingCart.objects.all().delete()
        Recipe.objects.all().delete()
        UserSubscription.objects.all().delete()
        
        # Clear user accounts but keep superusers
        User.objects.filter(is_superuser=False).delete()
        
        # Clear media files
        clear_media_files()
        
        return True
    except Exception as e:
        print(f"Error clearing user data: {e}")
        return False


def get_database_stats():
    """
    Get statistics about current database content.
    
    Returns:
        dict: Dictionary with counts of various objects
    """
    return {
        'users': User.objects.count(),
        'ingredients': Ingredient.objects.count(),
        'recipes': Recipe.objects.count(),
        'recipe_ingredients': RecipeIngredient.objects.count(),
        'favorites': Favorite.objects.count(),
        'shopping_carts': ShoppingCart.objects.count(),
        'subscriptions': UserSubscription.objects.count(),
        'tokens': Token.objects.count(),
    }


def print_database_stats():
    """Print current database statistics."""
    stats = get_database_stats()
    print("📊 Current Database Statistics:")
    print("-" * 30)
    for key, value in stats.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    print("-" * 30)


# Quick access functions
def quick_clear():
    """Quick clear function - clears everything."""
    return clear_database()


def quick_clear_data_only():
    """Quick clear function - data only, keep schema."""
    return clear_database(reset_counters=False, vacuum=False)


def quick_clear_user_data():
    """Quick clear function - user data only."""
    return clear_user_data_only()
