# Generated by Django 5.0.2 on 2025-06-02 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0005_alter_favorite_options_alter_shoppingcart_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='favorited_by',
        ),
        migrations.RemoveField(
            model_name='recipe',
            name='in_shopping_carts',
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(help_text='Unit of measurement (max 64 characters, e.g., grams, cups, pieces)', max_length=64, verbose_name='Measurement unit'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(help_text='Name of the ingredient (max 128 characters)', max_length=128, verbose_name='Ingredient name'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='name',
            field=models.CharField(help_text='Name of the recipe (max 256 characters)', max_length=256, verbose_name='Recipe name'),
        ),
    ]
