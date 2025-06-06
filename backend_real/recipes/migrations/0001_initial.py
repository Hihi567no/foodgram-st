# Generated by Django 5.0.2 on 2025-05-31 20:10

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the recipe', max_length=200, verbose_name='Recipe name')),
                ('image', models.ImageField(help_text='Image of the prepared dish', upload_to='recipes/images/', verbose_name='Recipe image')),
                ('text', models.TextField(help_text='Detailed cooking instructions', verbose_name='Recipe description')),
                ('cooking_time', models.PositiveSmallIntegerField(help_text='Time required to prepare the recipe in minutes', validators=[django.core.validators.MinValueValidator(1, message='Cooking time must be at least 1 minute'), django.core.validators.MaxValueValidator(32000, message='Cooking time cannot exceed 32000 minutes')], verbose_name='Cooking time (minutes)')),
                ('publication_date', models.DateTimeField(auto_now_add=True, verbose_name='Publication date')),
                ('is_published', models.BooleanField(default=True, help_text='Whether this recipe is visible to other users', verbose_name='Is published')),
            ],
            options={
                'verbose_name': 'Recipe',
                'verbose_name_plural': 'Recipes',
                'ordering': ['-publication_date'],
            },
        ),
        migrations.CreateModel(
            name='RecipeIngredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(help_text='Amount of ingredient needed', validators=[django.core.validators.MinValueValidator(1, message='Amount must be at least 1'), django.core.validators.MaxValueValidator(32000, message='Amount cannot exceed 32000')], verbose_name='Amount')),
            ],
            options={
                'verbose_name': 'Recipe ingredient',
                'verbose_name_plural': 'Recipe ingredients',
                'ordering': ['recipe', 'ingredient'],
            },
        ),
        migrations.CreateModel(
            name='UserFavoriteRecipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField(auto_now_add=True, verbose_name='Added to favorites')),
            ],
            options={
                'verbose_name': 'Favorite recipe',
                'verbose_name_plural': 'Favorite recipes',
                'ordering': ['-added_at'],
            },
        ),
        migrations.CreateModel(
            name='UserShoppingCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField(auto_now_add=True, verbose_name='Added to cart')),
            ],
            options={
                'verbose_name': 'Shopping cart item',
                'verbose_name_plural': 'Shopping cart items',
                'ordering': ['-added_at'],
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Name of the ingredient', max_length=200, verbose_name='Ingredient name')),
                ('measurement_unit', models.CharField(help_text='Unit of measurement (e.g., grams, cups, pieces)', max_length=200, verbose_name='Measurement unit')),
            ],
            options={
                'verbose_name': 'Ingredient',
                'verbose_name_plural': 'Ingredients',
                'ordering': ['name'],
                'indexes': [models.Index(fields=['name'], name='recipes_ing_name_164c6a_idx'), models.Index(fields=['measurement_unit'], name='recipes_ing_measure_95261a_idx')],
            },
        ),
        migrations.AddConstraint(
            model_name='ingredient',
            constraint=models.UniqueConstraint(fields=('name', 'measurement_unit'), name='unique_ingredient_measurement'),
        ),
    ]
