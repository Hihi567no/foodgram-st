from djoser.serializers import UserSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from recipes.models import Subscription
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Recipe


User = get_user_model()


class FoodgramUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(method_name="get_is_subscribed")
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "avatar",
        )

    def get_is_subscribed(self, author):
        request = self.context.get("request")
        return (
            request is not None 
            and not request.user.is_anonymous 
            and Subscription.objects.filter(user=request.user, author=author).exists()
        )

class ShortRecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = fields


class FoodgramUserWithRecipesSerializer(FoodgramUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(read_only=True, source="recipes.count")

    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
            "avatar",
        )

    def get_recipes(self, obj):
        request = self.context.get("request")
        recipes = obj.recipes.all()
        try:
            recipes_limit = int(request.query_params.get("recipes_limit"))
        except (ValueError, TypeError):
            pass
        else:
            recipes = recipes[:recipes_limit]

        return ShortRecipeSerializer(recipes, many=True).data


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(allow_null=True)

    class Meta:
        model = User
        fields = ("avatar",)