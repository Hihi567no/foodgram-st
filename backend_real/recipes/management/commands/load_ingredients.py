"""Management command to load ingredients from CSV / JSON files."""
import csv
import json
import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from recipes.models import Ingredient


class Command(BaseCommand):
    """Load ingredients from data files into the database."""

    help = 'Load ingredients from CSV or JSON files'

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            '--file',
            type=str,
            help='Path to the ingredients file (CSV or JSON)',
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['csv', 'json'],
            help='File format (csv or json)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing ingredients before loading',
        )

    def handle(self, *args, **options):
        """Execute the command logic."""
        self.stdout.write(
            self.style.SUCCESS('Starting ingredient loading process...')
        )

        if options['clear']:
            self.clear_ingredients()

        file_path = options.get('file')
        file_format = options.get('format')

        # If no file specified, try to find default files
        if not file_path:
            file_path, file_format = self.find_default_file()

        if not file_path:
            raise CommandError('No ingredient file found or specified')

        if not os.path.exists(file_path):
            raise CommandError(f'File not found: {file_path}')

        # Load ingredients based on format
        if file_format == 'csv':
            self.load_from_csv(file_path)
        elif file_format == 'json':
            self.load_from_json(file_path)
        else:
            raise CommandError('Unsupported file format')

        self.stdout.write(
            self.style.SUCCESS('Ingredient loading completed successfully!')
        )

    def find_default_file(self):
        """Find default ingredient files in the data directory."""
        data_dir = os.path.join(settings.BASE_DIR.parent, 'data')

        # Check for CSV file
        csv_path = os.path.join(data_dir, 'ingredients.csv')
        if os.path.exists(csv_path):
            return csv_path, 'csv'

        # Check for JSON file
        json_path = os.path.join(data_dir, 'ingredients.json')
        if os.path.exists(json_path):
            return json_path, 'json'

        return None, None

    def clear_ingredients(self):
        """Clear all existing ingredients."""
        count = Ingredient.objects.count()
        if count > 0:
            Ingredient.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f'Cleared {count} existing ingredients')
            )

    def load_from_csv(self, file_path):
        """Load ingredients from CSV file."""
        created_count = 0
        updated_count = 0
        skipped_count = 0

        with open(file_path, 'r', encoding='utf - 8') as csvfile:
            reader = csv.reader(csvfile)

            for row_num, row in enumerate(reader, 1):
                if len(row) != 2:
                    self.stdout.write(
                        self.style.WARNING(f'Skipping invalid row {row_num}: {row}')
                    )
                    skipped_count += 1
                    continue

                name = row[0].strip()
                measurement_unit = row[1].strip()

                if not name or not measurement_unit:
                    self.stdout.write(
                        self.style.WARNING(f'Skipping empty row {row_num}: {row}')
                    )
                    skipped_count += 1
                    continue

                ingredient, created = Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'CSV loading complete: {created_count} created, {updated_count} updated, {skipped_count} skipped'
            )
        )

    def load_from_json(self, file_path):
        """Load ingredients from JSON file."""
        created_count = 0
        updated_count = 0

        with open(file_path, 'r', encoding='utf - 8') as jsonfile:
            data = json.load(jsonfile)

            for item in data:
                name = item.get('name', '').strip()
                measurement_unit = item.get('measurement_unit', '').strip()

                if not name or not measurement_unit:
                    self.stdout.write(
                        self.style.WARNING(f'Skipping invalid item: {item}')
                    )
                    continue

                ingredient, created = Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'JSON loading complete: {created_count} created, {updated_count} updated'
            )
        )
