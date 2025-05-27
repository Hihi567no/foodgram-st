"""Сериализаторы для приложения users."""
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from users.models import CustomUser, Subscription
from recipes.models import Recipe


class CustomUserSerializer(UserSerializer):
    """Сериализатор для модели CustomUser"""
    
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta(UserSerializer.Meta):
        """Мета-класс для UserSerializer."""
        
        model = CustomUser
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'avatar', 'is_subscribed')

    def get_is_subscribed(self, obj):
        """Проверяет, подписан ли запросивший пользователь."""
        
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscription.objects.filter(user=user, following=obj).exists()

    def get_avatar(self, obj):
        """Возвращает абсолютный URL для аватара."""
        
        if obj.avatar:
            return obj.avatar.url
        return None


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления аватара пользователя."""
    
    avatar = Base64ImageField(required=True)

    class Meta:
        """Мета-класс для UserAvatarSerializer."""
        
        model = CustomUser
        fields = ('avatar',)

    def update(self, instance, validated_data):
        """Возвращает абсолютный URL для аватара."""
        avatar = validated_data.get('avatar')
        if avatar is None:
            raise serializers.ValidationError(
                {'avatar': 'Avatar is required.'}
            )

        instance.avatar = avatar
        instance.save()
        return instance


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class SubscriptionUserSerializer(serializers.ModelSerializer):
    """ Сериализатор для пользователя подписки. """
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        """" Мета-класс для подписки пользователя. """
        
        model = CustomUser
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes', 'recipes_count', 'avatar'
        )

    def get_is_subscribed(self, obj):
        return True

    def get_recipes(self, obj):
        """Возвращает список рецептов подписанного пользователя."""	
        request = self.context.get('request')
        try:
            limit = int(request.query_params.get('recipes_limit'))
        except (ValueError, TypeError):
            limit = None
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:limit]
        return ShortRecipeSerializer(recipes, many=True, context=self.context).data

    def get_recipes_count(self, obj):
        """Возвращает количество рецептов подписанного пользователя."""
        return obj.recipes.count()
