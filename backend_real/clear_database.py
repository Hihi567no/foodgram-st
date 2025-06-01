#!/usr/bin/env python
"""
Script to clear the entire database.
This will delete ALL data from all tables.

Usage:
    python clear_database.py

WARNING: This will permanently delete all data!
"""
import os
import sys
import django
from django.core.management.color import no_style
from django.db import connection

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram_backend.settings')
django.setup()

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


def confirm_deletion():
    """Ask user for confirmation before deleting data."""
    print("⚠️  WARNING: This will permanently delete ALL data from the database!")
    print("This includes:")
    print("  - All users and their profiles")
    print("  - All recipes and ingredients")
    print("  - All favorites and shopping carts")
    print("  - All subscriptions")
    print("  - All authentication tokens")
    print("  - All admin logs and sessions")
    print()
    
    response = input("Are you sure you want to continue? Type 'YES' to confirm: ")
    return response.strip() == 'YES'


def clear_media_files():
    """Clear uploaded media files."""
    import shutil
    from django.conf import settings
    
    media_root = settings.MEDIA_ROOT
    if os.path.exists(media_root):
        print(f"Clearing media files from: {media_root}")
        try:
            # Remove all files and subdirectories
            for filename in os.listdir(media_root):
                file_path = os.path.join(media_root, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            print("✅ Media files cleared successfully")
        except Exception as e:
            print(f"❌ Error clearing media files: {e}")
    else:
        print("📁 Media directory doesn't exist")


def clear_database_data():
    """Clear all data from database tables."""
    print("🗑️  Clearing database data...")
    
    try:
        # Clear application data in dependency order
        print("  - Clearing recipe ingredients...")
        RecipeIngredient.objects.all().delete()
        
        print("  - Clearing favorites...")
        Favorite.objects.all().delete()
        
        print("  - Clearing shopping carts...")
        ShoppingCart.objects.all().delete()
        
        print("  - Clearing recipes...")
        Recipe.objects.all().delete()
        
        print("  - Clearing ingredients...")
        Ingredient.objects.all().delete()
        
        print("  - Clearing user subscriptions...")
        UserSubscription.objects.all().delete()
        
        print("  - Clearing authentication tokens...")
        Token.objects.all().delete()
        
        print("  - Clearing admin logs...")
        LogEntry.objects.all().delete()
        
        print("  - Clearing sessions...")
        Session.objects.all().delete()
        
        print("  - Clearing users...")
        User.objects.all().delete()
        
        print("  - Clearing content types...")
        ContentType.objects.all().delete()
        
        print("✅ Database data cleared successfully")
        
    except Exception as e:
        print(f"❌ Error clearing database data: {e}")
        return False
    
    return True


def reset_auto_increment():
    """Reset auto-increment counters for all tables."""
    print("🔄 Resetting auto-increment counters...")
    
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
            
        print("✅ Auto-increment counters reset successfully")
        
    except Exception as e:
        print(f"❌ Error resetting auto-increment: {e}")


def vacuum_database():
    """Vacuum the database to reclaim space."""
    print("🧹 Vacuuming database...")
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("VACUUM")
        print("✅ Database vacuumed successfully")
        
    except Exception as e:
        print(f"❌ Error vacuuming database: {e}")


def clear_all():
    """Clear everything: database data and media files."""
    print("🚀 Starting complete database clear...")
    print("=" * 50)
    
    # Clear database data
    if clear_database_data():
        # Reset auto-increment counters
        reset_auto_increment()
        
        # Vacuum database
        vacuum_database()
        
        # Clear media files
        clear_media_files()
        
        print("=" * 50)
        print("✅ Database cleared completely!")
        print("\n📝 Next steps:")
        print("  1. Run migrations: python manage.py migrate")
        print("  2. Create superuser: python manage.py createsuperuser")
        print("  3. Set up test data: python setup_test_data.py")
        
    else:
        print("❌ Database clear failed!")
        return False
    
    return True


def clear_data_only():
    """Clear only data, keep schema intact."""
    print("🚀 Starting data-only clear...")
    print("=" * 50)
    
    if clear_database_data():
        reset_auto_increment()
        clear_media_files()
        
        print("=" * 50)
        print("✅ Database data cleared!")
        print("\n📝 Next steps:")
        print("  1. Set up test data: python setup_test_data.py")
        
    else:
        print("❌ Data clear failed!")
        return False
    
    return True


def main():
    """Main function with user interaction."""
    print("🗃️  Database Clear Utility")
    print("=" * 50)
    
    if not confirm_deletion():
        print("❌ Operation cancelled by user")
        return
    
    print("\nChoose clearing option:")
    print("1. Clear data only (keep schema)")
    print("2. Clear everything (data + reset)")
    
    choice = input("\nEnter your choice (1 or 2): ").strip()
    
    if choice == "1":
        clear_data_only()
    elif choice == "2":
        clear_all()
    else:
        print("❌ Invalid choice. Operation cancelled.")


if __name__ == '__main__':
    main()
