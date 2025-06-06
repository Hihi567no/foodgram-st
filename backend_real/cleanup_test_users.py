import os
import django

# Setup Django environment first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram_backend.settings')
django.setup()

# Now import Django models after setup
from django.db import models  # noqa: E402
from users.models import User  # noqa: E402


def cleanup_test_users():

    print("Current users in database:")
    for user in User.objects.all():
        print(
            f"  ID: {user.id}, Username: {user.username}, Email: {user.email}, Superuser: {user.is_superuser}")

    test_users = User.objects.filter(
        models.Q(email__contains='test_')
        | models.Q(username__contains='testuser_')
    )

    if test_users.exists():
        count = test_users.count()
        test_users.delete()
        print(f"\n✅ Deleted {count} test users")
    else:
        print("\n✅ No test users found to delete")

    print("\nRemaining users:")
    for user in User.objects.all():
        print(
            f"  ID: {user.id}, Username: {user.username}, Email: {user.email}")


if __name__ == "__main__":
    cleanup_test_users()
