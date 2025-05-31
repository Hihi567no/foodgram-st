from django.db import models
from users.models import User
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'foodgram_backend.settings')
django.setup()


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
