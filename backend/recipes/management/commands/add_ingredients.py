from django.core.management.base import BaseCommand
from django.db import transaction
import json

from recipes.models import Ingredient


class Command(BaseCommand):
    help = "Fill Ingredient table with data from json"

    def handle(self, *args, **options):
        with open(options["json_file_path"], "r") as json_file:
            ingredients = json.load(json_file)
        ingredients = [Ingredient(**ingredient) for ingredient in ingredients]
        with transaction.atomic():
            Ingredient.objects.bulk_create(ingredients)

    def add_arguments(self, parser): 
        parser.add_argument("json_file_path", help="Json file path")