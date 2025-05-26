from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import transaction
from recipes.models import Recipe, IngredientInRecipe, FavoriteRecipe, ShoppingCart
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Ingredient
from ..users.serializers import FoodgramUserSerializer


User = get_user_model()


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True
    )
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    image = Base64ImageField()
    ingredients = IngredientInRecipeSerializer(many=True, source="recipe_ingredients")
    author = FoodgramUserSerializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )


    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError("Изображение не может быть пустым.")
        return value

    def validate(self, attrs):
        ingredients = attrs.get("recipe_ingredients", [])
        if len(ingredients) == 0:
            raise serializers.ValidationError(
                "Должен быть указан хотя бы один ингредиент."
            )
        ingredients_ids = [item["id"].id for item in ingredients]
        if len(ingredients) > len(set(ingredients_ids)):
            raise serializers.ValidationError("Ингредиенты не должны повторяться.")
        return attrs

    def get_is_favorited(self, recipe):
        current_user = self.context["request"].user
        if current_user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(user=current_user, recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        current_user = self.context["request"].user
        if current_user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(user=current_user, recipe=recipe).exists()

    def bulk_create_ingredients(self, ingredients, recipe):
        IngredientInRecipe.objects.bulk_create([
            IngredientInRecipe(
                recipe=recipe,
                ingredient=item["id"],
                amount=item["amount"],
            )
            for item in ingredients
        ]) 

    def create(self, validated_data):
        ingredients = validated_data.pop("recipe_ingredients")
        with transaction.atomic():
            validated_data["author"] = self.context["request"].user # без этой строки не добавится автор, его нет в validate_data по умолчанию
            recipe = super().create(validated_data)
            self.bulk_create_ingredients(ingredients, recipe)
            return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop("recipe_ingredients")
        with transaction.atomic():
            instance.ingredients.clear()
            self.bulk_create_ingredients(ingredients, instance)
        return super().update(instance, validated_data)
