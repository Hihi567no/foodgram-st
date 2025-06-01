"""API serializers for the Foodgram application."""
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer as DjoserUserSerializer
from rest_framework import serializers

from users.models import UserSubscription
from recipes.models import (
    Ingredient, Recipe, RecipeIngredient,
    Favorite, ShoppingCart
)
from foodgram_backend import constants
from .fields import Base64ImageField

User = get_user_model()


def check_user_relation(context, obj, relation_name):
    """Universal method to check user relations."""
    request = context.get('request')
    if not (request and request.user.is_authenticated):
        return False

    # Check if user has relation with this recipe
    if relation_name == 'favorites':
        return obj.favorites.filter(user=request.user).exists()
    elif relation_name == 'shoppingcarts':
        return obj.shoppingcarts.filter(user=request.user).exists()

    return False


class UserRegistrationSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields + ('first_name', 'last_name')

    def validate_username(self, value):
        import re
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError(
                'Enter a valid username. This value may contain only letters, '
                'numbers, and @/./+/-/_ characters.'
            )
        return value


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
        request = self.context.get('request')
        return (request and
                request.user.is_authenticated and
                obj.followers.filter(subscriber=request.user).exists())

    def get_avatar(self, obj):
        if not obj.avatar or not hasattr(obj.avatar, 'url'):
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.avatar.url)
        return obj.avatar.url


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
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        error_messages={'does_not_exist': 'Ingredient with id {pk_value} does not exist.'}
    )
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

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'name', 'image', 'text',
            'ingredients', 'cooking_time',
            'is_favorited', 'is_in_shopping_cart'
        )

    def get_is_favorited(self, obj):
        return check_user_relation(self.context, obj, 'favorites')

    def get_is_in_shopping_cart(self, obj):
        return check_user_relation(self.context, obj, 'shoppingcarts')


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating recipes."""

    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField()
    name = serializers.CharField(
        max_length=constants.MAX_RECIPE_NAME_LENGTH,
        required=True,
        allow_blank=False
    )
    text = serializers.CharField(
        required=True,
        allow_blank=False
    )
    cooking_time = serializers.IntegerField(
        min_value=constants.MIN_COOKING_TIME,
        max_value=constants.MAX_COOKING_TIME,
        required=True
    )

    class Meta:
        model = Recipe
        fields = (
            'name', 'image', 'text', 'ingredients', 'cooking_time'
        )

    def validate_image(self, value):
        """Validate image field - cannot be empty."""
        if not value:
            raise serializers.ValidationError("Image field cannot be empty.")
        return value

    def validate_cooking_time(self, value):
        """Validate cooking time - must be a positive integer."""
        if value is None:
            raise serializers.ValidationError("Cooking time is required.")
        if not isinstance(value, int) or value < constants.MIN_COOKING_TIME:
            raise serializers.ValidationError(
                f"Cooking time must be at least {constants.MIN_COOKING_TIME} minute(s)."
            )
        return value

    def validate(self, data):
        ingredients = data.get('ingredients', [])
        if not ingredients:
            raise serializers.ValidationError({
                'ingredients': 'At least one ingredient is required.'
            })

        ingredient_ids = [item['id'].id for item in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError({
                'ingredients': 'Duplicate ingredients are not allowed.'
            })

        return data

    def create(self, validated_data):
        """Create a new recipe with ingredients."""
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)

        self._create_recipe_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')

        instance = super().update(instance, validated_data)

        instance.recipe_ingredients.all().delete()
        self._create_recipe_ingredients(instance, ingredients_data)

        return instance

    def _create_recipe_ingredients(self, recipe, ingredients_data):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient_data['id'].id,
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredients_data
        )

    def to_representation(self, instance):
        """Return recipe representation using RecipeSerializer."""
        return RecipeSerializer(instance, context=self.context).data


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = fields


class UserSubscriptionListSerializer(UserProfileSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta(UserProfileSerializer.Meta):
        fields = UserProfileSerializer.Meta.fields + ('recipes_count', 'recipes')

    def get_is_subscribed(self, obj):
        """Always return True for subscription list serializer."""
        return True

    def get_recipes(self, obj):
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


class FavoriteSerializer(serializers.ModelSerializer):
    """Serializer for adding/removing recipes from favorites."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        """Validate favorite data."""
        user = data['user']
        recipe = data['recipe']

        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                "Recipe is already in favorites."
            )
        return data

    def to_representation(self, instance):
        """Return recipe representation."""
        return RecipeMinifiedSerializer(
            instance.recipe,
            context=self.context
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Serializer for adding/removing recipes from shopping cart."""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        """Validate shopping cart data."""
        user = data['user']
        recipe = data['recipe']

        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                "Recipe is already in shopping cart."
            )
        return data

    def to_representation(self, instance):
        """Return recipe representation."""
        return RecipeMinifiedSerializer(
            instance.recipe,
            context=self.context
        ).data


class UserSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for creating/managing user subscriptions."""

    class Meta:
        model = UserSubscription
        fields = ('subscriber', 'target_user')

    def validate(self, data):
        """Validate subscription data."""
        subscriber = data['subscriber']
        target_user = data['target_user']

        # Check if user tries to subscribe to themselves
        if subscriber == target_user:
            raise serializers.ValidationError(
                "Cannot subscribe to yourself."
            )

        # Check if subscription already exists
        if UserSubscription.objects.filter(
            subscriber=subscriber,
            target_user=target_user
        ).exists():
            raise serializers.ValidationError(
                "Already subscribed to this user."
            )

        return data

    def to_representation(self, instance):
        """Return user representation with subscription info."""
        return UserSubscriptionListSerializer(
            instance.target_user,
            context=self.context
        ).data
