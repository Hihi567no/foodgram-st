""" Сериализаторы для приложения recipes. """
from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from users.serializers import CustomUserSerializer
from .models import (Favorite, Ingredient, IngredientInRecipe,
                     Recipe, ShoppingCart)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        """Мета-класс для IngredientSerializer."""
        
        model = Ingredient
        fields = '__all__'
        read_only_fields = ('id',)


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для связи ингредиента и рецепта."""
    
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
        read_only=True
    )

    class Meta:
        """Мета-класс для IngredientInRecipeSerializer."""
        
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов."""
    
    ingredients = IngredientInRecipeSerializer(
        source='ingredient_amounts',
        many=True
    )
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(required=False)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        """Мета-класс для RecipeSerializer."""
        
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )
        read_only_fields = ('id', 'author', 'is_favorited',
                            'is_in_shopping_cart')

    @transaction.atomic
    def create(self, validated_data):
        """Возвращает созданный рецепт."""
        
        ingredient_data = validated_data.pop('ingredient_amounts')
        recipe = Recipe.objects.create(**validated_data)
        self._set_ingredients(recipe, ingredient_data)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        """Возвращает обновленный рецепт."""
        
        ingredient_data = validated_data.pop('ingredient_amounts', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if ingredient_data is not None:
            instance.ingredient_amounts.all().delete()
            self._set_ingredients(instance, ingredient_data)
        return instance

    def _set_ingredients(self, recipe, ingredient_data):
        """Добавляет в рецепт ингредиенты."""
        
        IngredientInRecipe.objects.bulk_create([
            IngredientInRecipe(
                recipe=recipe,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount']
            )
            for ingredient_data in ingredient_data
        ])

    # Ошибка, если поле image есть, но у него пустое значение
    def validate_image(self, value):
        """Проверяет, что картинка не пустая."""
        
        if not value:
            raise serializers.ValidationError('У рецепта должна быть картинка')
        return value

    def validate(self, data):
        """Проверяет, что в рецепте есть хотя бы один ингредиент."""
        
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'У рецепта должен быть хотя бы один ингредиент'}
            )

        seen_ingredients = set()
        for ingr in ingredients:
            ingr_id = ingr.get('id')
            ingr_amount = ingr.get('amount')

            if ingr_id in seen_ingredients:
                raise serializers.ValidationError(
                    {'ingredients': 'Ингредиенты должны быть уникальными'}
                )
            seen_ingredients.add(ingr_id)

            if int(ingr_amount) <= 0:
                raise serializers.ValidationError(
                    {'ingredients': 'Количество ингредиента должно быть больше нуля'}
                )
            
        # Проверка только в случае создания рецепта (не нарушает редактирование)
        if self.instance is None:
            image_in_data = 'image' in self.initial_data
            image_value = self.initial_data.get('image')
            
            if not image_in_data or not image_value:
                raise serializers.ValidationError(
                    {'image': 'У рецепта должна быть картинка'}
                )
            
        return data

    def get_is_favorited(self, obj):
        """Возвращает True, если пользователь избрал рецепт."""
        
        request = self.context.get('request')
        return Favorite.objects.filter(
            user=request.user.id,
            recipe=obj
        ).exists()

    def get_is_in_shopping_cart(self, obj):
        """Возвращает True, если пользователь добавил рецепт в корзину."""
        
        request = self.context.get('request')
        return ShoppingCart.objects.filter(
            user=request.user.id,
            recipe=obj
        ).exists()

    def to_representation(self, instance):
        """Возвращает рецепт в виде словаря."""
        
        representation = super().to_representation(instance)
        representation['image'] = instance.image.url
        return representation
