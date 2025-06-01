#!/usr/bin/env python
"""
Setup script for running Foodgram backend locally with SQLite.
This script automates the setup process for local development.
"""
import sys
import subprocess
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"Error: {e.stderr}")
        return False


def create_env_file():
    """Create .env file for local development."""
    env_content = """# Local development with SQLite
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=local-development-secret-key-change-in-production
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,*

# PostgreSQL settings (ignored when DEBUG=True)
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
"""
    
    env_path = Path('.env')
    if env_path.exists():
        print("📝 .env file already exists, skipping creation")
        return True
    
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        print("✅ Created .env file for local development")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False


def main():
    """Main setup function."""
    print("🍽️ Foodgram Backend Local Setup with SQLite")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path('manage.py').exists():
        print("❌ Error: manage.py not found. Please run this script from the backend_real directory.")
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        sys.exit(1)
    
    # Run setup commands
    setup_commands = [
        ("python manage.py makemigrations users recipes", "Creating migrations"),
        ("python manage.py migrate", "Applying database migrations"),
        ("python manage.py load_ingredients", "Loading ingredients data"),
        ("python manage.py load_initial_data", "Loading sample data"),
        ("python manage.py collectstatic --noinput", "Collecting static files"),
    ]
    
    for command, description in setup_commands:
        if not run_command(command, description):
            print(f"\n❌ Setup failed at: {description}")
            print("Please check the error messages above and try again.")
            sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Create a superuser (optional):")
    print("   python manage.py createsuperuser")
    print("\n2. Start the development server:")
    print("   python manage.py runserver")
    print("\n3. Access your application:")
    print("   - API: http://localhost:8000/api/")
    print("   - Admin: http://localhost:8000/admin/")
    print("\n📁 Database file: db.sqlite3")
    print("📁 Media files: media/")
    print("📁 Static files: collected_static/")


if __name__ == "__main__":
    main()
