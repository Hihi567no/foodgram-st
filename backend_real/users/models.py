"""User models with enhanced functionality and custom managers."""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils import timezone
from django.core.validators import EmailValidator

from foodgram_backend.constants import (
    MAX_USERNAME_LENGTH, MAX_EMAIL_LENGTH, MAX_NAME_LENGTH
)


class UserAccountManager(BaseUserManager):
    """Custom manager for User model with email-based authentication."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        if not email:
            raise ValueError('Email address is required')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

    def active_users(self):
        """Return only active users."""
        return self.filter(is_active=True)

    def with_recipes(self):
        """Return users who have created at least one recipe."""
        return self.filter(recipes__isnull=False).distinct()


class User(AbstractUser):
    """Enhanced user model with email as the primary identifier."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    email = models.EmailField(
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
        validators=[EmailValidator()],
        verbose_name='Email address',
        help_text=f'Required. Enter a valid email address (max {MAX_EMAIL_LENGTH} characters).'
    )
    first_name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='First name',
        help_text=f'User\'s first name (max {MAX_NAME_LENGTH} characters)'
    )
    last_name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Last name',
        help_text=f'User\'s last name (max {MAX_NAME_LENGTH} characters)'
    )
    username = models.CharField(
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
        validators=[UnicodeUsernameValidator()],
        verbose_name='Username',
        help_text=f'Required. {MAX_USERNAME_LENGTH} characters or fewer. Letters, digits and @/./+/-/_ only.'
    )
    avatar = models.ImageField(
        upload_to='users/avatars/',
        blank=True,
        null=True,
        verbose_name='Profile picture',
        help_text='Optional profile picture'
    )
    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name='Date joined'
    )

    objects = UserAccountManager()

    class Meta:
        """Meta options for User model."""
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['username']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
        ]

    def __str__(self):
        """String representation of the user."""
        return self.email

    @property
    def full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name


class UserSubscription(models.Model):
    """Model for user subscriptions (following system)."""

    subscriber = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Subscriber',
        help_text='User who is following'
    )
    target_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        verbose_name='Target user',
        help_text='User being followed'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Subscription date'
    )

    class Meta:
        """Meta options for UserSubscription model."""
        verbose_name = 'User subscription'
        verbose_name_plural = 'User subscriptions'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['subscriber', 'target_user'],
                name='unique_user_subscription'
            ),
            models.CheckConstraint(
                check=~models.Q(subscriber=models.F('target_user')),
                name='prevent_self_subscription'
            )
        ]
        indexes = [
            models.Index(fields=['subscriber']),
            models.Index(fields=['target_user']),
        ]

    def __str__(self):
        """String representation of the subscription."""
        return f'{self.subscriber.username} follows {self.target_user.username}'
