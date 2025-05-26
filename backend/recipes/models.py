from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.core.validators import RegexValidator



class Ingredient(models.Model):
    name = models.CharField("Название", max_length=128, db_index=True)
    measurement_unit = models.CharField("Единица измерения", max_length=64)

    class Meta:
        ordering = ("name",)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="name_measurement_unit",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.measurement_unit})"


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=(RegexValidator(regex=r'^[\w.@+-]+\Z'),),
        verbose_name="Никнейм пользователя",
    )
    email = models.EmailField(
        unique=True,
        max_length=254,
        verbose_name="email",
        help_text="Введите адрес электронной почты",
    )
    avatar = models.ImageField(
        upload_to="users/images/",
        null=True,
        default=None,
        blank=True,
        verbose_name="Аватар",
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("-date_joined",)

    def __str__(self):
        return self.username


class Recipe(models.Model):
    name = models.CharField("Название", max_length=256)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recipes", verbose_name="Автор"
    )
    image = models.ImageField(
        upload_to="recipes/images/",
        null=False,
        default=None,
        verbose_name="Изображение",
    )
    text = models.TextField("Описание")
    cooking_time = models.IntegerField(
        "Время приготовления в минутах",
        validators=[
            MinValueValidator(
                1,
            )
        ],
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name="Ингредиенты",
        through="IngredientInRecipe",
        related_name="recipes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепт"
        ordering = ("-created_at",)

    def __str__(self):
        return self.name


class UserRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь"
    )

    class Meta:
        abstract = True


class FavoriteRecipe(UserRecipe):
    class Meta():
        constraints = (
            models.UniqueConstraint(fields=("user", "recipe"), name="unique_favorite_user_recipe"),
        )
        default_related_name = "favorites"
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"


class ShoppingCart(UserRecipe):
    class Meta():
        constraints = (
            models.UniqueConstraint(fields=("user", "recipe"), name="unique_shopping_cart_user_recipe"),
        )
        default_related_name = "shopping_carts"
        verbose_name = "Рецепт в корзине"
        verbose_name_plural = "Рецепты в корзине"


class IngredientInRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name="Ингредиент"
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name="Рецепт")
    amount = models.PositiveIntegerField(
        "Количество",
        validators=(MinValueValidator(1),)
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=("ingredient", "recipe"), name="unique_ingredient_recipe"),
        )
        default_related_name = "recipe_ingredients"
        verbose_name = "Продукт в составе рецепта"
        verbose_name_plural = "Продукты в составе рецептов"
        


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="authors",
        # при обращении к полю authors объекта класса User ожидается получение всех авторов,
        # на которых он подписан, related_name позволит нам получить все строки таблицы, где в колонке user
        # располагается текущий объект, так как поле user - подписчик, получится, что были получены все авторы
        # поэтому здесь в качестве related_name указано значение authors
        verbose_name="Подписчик",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followers",
        # при обращении к полю followers объекта класса User ожидается получение всех подписчиков,
        # related_name позволит нам получить все строки таблицы, где в колонке author
        # располагается текущий объект, так как поле author - автор, получится, что были получены все подписчики
        # поэтому здесь в качестве related_name указано значение followers
        verbose_name="Отслеживаемый автор",
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(fields=("user", "author"), name="unique_following"),
        )
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self):
        return f"{self.user} follows {self.author}"
