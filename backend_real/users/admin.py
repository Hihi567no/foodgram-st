"""Admin configuration for user management."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from .models import User, UserSubscription


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Enhanced admin interface for User model."""

    list_display = (
        'email', 'username', 'full_name', 'is_active',
        'is_staff', 'date_joined', 'recipe_count'
    )
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username',
         'first_name', 'last_name', 'avatar')}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )

    readonly_fields = ('date_joined', 'last_login')

    def full_name(self, obj):
        """Display user's full name."""
        return obj.full_name
    full_name.short_description = 'Full Name'

    def recipe_count(self, obj):
        """Display number of recipes created by user."""
        count = obj.recipes.count()
        return format_html('<strong>{}</strong>', count)
    recipe_count.short_description = 'Recipes'


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    """Admin interface for UserSubscription model."""

    list_display = ('subscriber', 'target_user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('subscriber__username', 'target_user__username')
    ordering = ('-created_at',)

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('subscriber', 'target_user')
