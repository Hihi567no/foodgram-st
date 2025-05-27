""" Модели для приложения recipes. """
from django.db import models
from django.core.validators import MinValueValidator

from users.models import CustomUser


INGREDIENT_NAME_MAX_LENGTH = 128
RECIPE_NAME_MAX_LENGTH = 256
UNIT_MAX_LENGTH = 64
MIN_INGREDIENT_AMOUNT = 1
MIN_COOKING_TIME = 1

class Ingredient(models.Model):
    """ Модель для ингредиентов. """

    name = models.CharField(
        "Название", max_length=INGREDIENT_NAME_MAX_LENGTH, unique=True
    )
    measurement_unit = models.CharField("Единица измерения", max_length=UNIT_MAX_LENGTH)

    class Meta:
        ordering = ["name"]
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """ Модель для рецептов. """

    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="recipes"
    )
    name = models.CharField("Название", max_length=RECIPE_NAME_MAX_LENGTH)
    image = models.ImageField("Фото", upload_to="recipes/")
    text = models.TextField("Описание")
    cooking_time = models.PositiveSmallIntegerField(
        "Время приготовления", validators=[MinValueValidator(MIN_COOKING_TIME)]
    )
    ingredients = models.ManyToManyField(Ingredient, through="IngredientInRecipe")

    class Meta:
        ordering = ["name"]
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """ Связь между ингредиентом и рецептом. """

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="ingredient_amounts"
    )
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        "Колчиество", validators=[MinValueValidator(MIN_INGREDIENT_AMOUNT)]
    )


class Favorite(models.Model):
    """ Модель для избранных рецептов. """
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="favorites"
    )

    class Meta:
        verbose_name = ("Избранное",)
        verbose_name_plural = "Избранные"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique user recipe"
            )
        ]


class ShoppingCart(models.Model):
    """ Модель для корзины. """
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="in_cart")

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique user recipe shopping_cart"
            )
        ]
