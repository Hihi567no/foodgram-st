"""API serializers for the Foodgram application."""
import base64
import uuid

from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer as DjoserUserSerializer
from rest_framework import serializers

from users.models import UserSubscription
from recipes.models import (
    Ingredient, Recipe, RecipeIngredient,
    UserFavoriteRecipe, UserShoppingCart
)
from foodgram_backend import constants

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Custom field for handling base64 encoded images."""

    def to_internal_value(self, data):
        """Convert base64 string to image file."""
        if isinstance(data, str) and data.startswith('data:image'):
            # Extract format and base64 data
            format_part, imgstr = data.split(';base64,')
            ext = format_part.split('/')[-1]

            # Generate unique filename
            filename = f'{uuid.uuid4()}.{ext}'

            # Create file from base64 data
            data = ContentFile(base64.b64decode(imgstr), name=filename)

        return super().to_internal_value(data)


class UserRegistrationResponseSerializer(serializers.ModelSerializer):
    """Serializer for user registration response (only required fields)."""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')
        read_only_fields = fields


class UserRegistrationSerializer(UserCreateSerializer):
    """Serializer for user registration."""

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')

    def validate_username(self, value):
        """Validate username format."""
        import re
        # Django's default username validator pattern
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError(
                'Enter a valid username. This value may contain only letters, '
                'numbers, and @/./+/-/_ characters.'
            )
        return value

    def to_representation(self, instance):
        """Return only the required fields for registration response."""
        return UserRegistrationResponseSerializer(instance, context=self.context).data


class UserProfileSerializer(DjoserUserSerializer):
    """Serializer for user profile information."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'avatar'
        )

    def get_is_subscribed(self, obj):
        """Check if current user is subscribed to this user."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False

        return UserSubscription.objects.filter(
            subscriber=request.user,
            target_user=obj
        ).exists()

    def get_avatar(self, obj):
        """Get avatar URL or null."""
        request = self.context.get('request')
        if obj.avatar and hasattr(obj.avatar, 'url'):
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None  # This will be serialized as null in JSON


class UserAvatarSerializer(serializers.ModelSerializer):
    """Serializer for updating user avatar."""

    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredient information."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Serializer for recipe ingredients with amounts."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating recipe ingredients."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        min_value=constants.MIN_INGREDIENT_AMOUNT,
        max_value=constants.MAX_INGREDIENT_AMOUNT
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipe information (read-only)."""

    author = UserProfileSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipe_ingredients',
        many=True,
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'name', 'image', 'text',
            'ingredients', 'cooking_time',
            'is_favorited', 'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        """Check if recipe is in user's favorites."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False

        return UserFavoriteRecipe.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """Check if recipe is in user's shopping cart."""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False

        return UserShoppingCart.objects.filter(
            user=request.user,
            recipe=obj
        ).exists()

    def get_image(self, obj):
        """Get image URL."""
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return ""


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating recipes."""

    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        min_value=constants.MIN_COOKING_TIME,
        max_value=constants.MAX_COOKING_TIME
    )

    class Meta:
        model = Recipe
        fields = (
            'name', 'image', 'text', 'ingredients', 'cooking_time'
        )

    def validate_ingredients(self, value):
        """Validate ingredients data."""
        if not value:
            raise serializers.ValidationError(
                'At least one ingredient is required.')

        ingredient_ids = [item['id'] for item in value]

        # Check for duplicates
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Duplicate ingredients are not allowed.')

        # Check if all ingredients exist
        existing_ingredients = Ingredient.objects.filter(id__in=ingredient_ids)
        if len(existing_ingredients) != len(ingredient_ids):
            raise serializers.ValidationError('Some ingredients do not exist.')

        return value

    def create(self, validated_data):
        """Create a new recipe with ingredients."""
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)

        self._create_recipe_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        """Update recipe and its ingredients."""
        ingredients_data = validated_data.pop('ingredients', None)

        # For updates, ingredients are required
        if ingredients_data is None:
            raise serializers.ValidationError(
                {'ingredients': ['This field is required.']})

        # Update recipe fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update ingredients
        instance.recipe_ingredients.all().delete()
        self._create_recipe_ingredients(instance, ingredients_data)

        return instance

    def _create_recipe_ingredients(self, recipe, ingredients_data):
        """Helper method to create recipe ingredients."""
        recipe_ingredients = []

        for ingredient_data in ingredients_data:
            ingredient = Ingredient.objects.get(id=ingredient_data['id'])
            recipe_ingredients.append(
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient,
                    amount=ingredient_data['amount']
                )
            )

        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def to_representation(self, instance):
        """Return recipe representation using RecipeSerializer."""
        return RecipeSerializer(instance, context=self.context).data


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    """Minimal recipe serializer for lists and references."""

    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields

    def get_image(self, obj):
        """Get image URL or empty string (never null)."""
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return ""  # Always return string, never null


class UserSubscriptionListSerializer(serializers.ModelSerializer):
    """Serializer for listing user subscriptions."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email',
            'is_subscribed', 'avatar', 'recipes_count', 'recipes'
        )

    def get_is_subscribed(self, obj):
        """Always True for subscription lists."""
        return True

    def get_avatar(self, obj):
        """Get avatar URL or null."""
        request = self.context.get('request')
        if obj.avatar and hasattr(obj.avatar, 'url'):
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None  # This will be serialized as null in JSON

    def get_recipes(self, obj):
        """Get limited list of user's recipes."""
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')

        recipes = obj.recipes.all()
        if recipes_limit:
            try:
                limit = int(recipes_limit)
                if limit > 0:
                    recipes = recipes[:limit]
            except (ValueError, TypeError):
                pass

        return RecipeMinifiedSerializer(recipes, many=True, context=self.context).data

    def get_recipes_count(self, obj):
        """Get total count of user's recipes."""
        return obj.recipes.count()


class UserSubscriptionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating user subscriptions."""

    class Meta:
        model = UserSubscription
        fields = ('subscriber', 'target_user')

    def validate(self, data):
        """Validate subscription data."""
        subscriber = data['subscriber']
        target_user = data['target_user']

        if subscriber == target_user:
            raise serializers.ValidationError("Cannot subscribe to yourself.")

        if UserSubscription.objects.filter(
            subscriber=subscriber,
            target_user=target_user
        ).exists():
            raise serializers.ValidationError(
                "Already subscribed to this user.")

        return data

    def to_representation(self, instance):
        """Return user representation with subscription info."""
        return UserSubscriptionListSerializer(
            instance.target_user,
            context=self.context
        ).data
