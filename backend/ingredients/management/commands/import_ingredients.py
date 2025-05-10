import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from ingredients.models import Ingredient


class Command(BaseCommand):
    help = 'Загружает ингредиенты из JSON-файла в базу данных'
    file_name = 'ingredients.json'

    def handle(self, *args, **options):
        file_path = self.get_ingredient_file_path()

        if not file_path.exists():
            self.report_file_missing(file_path)
            return

        try:
            items = self.read_json_data(file_path)
            inserted = self.insert_ingredients(items)
            self.stdout.write(self.style.SUCCESS(
                f'Добавлено новых записей: {inserted}'
            ))
        except Exception as exc:
            self.stderr.write(self.style.ERROR(
                f'Произошла ошибка во время обработки: {exc}'
            ))

    def get_ingredient_file_path(self):
        return Path(settings.BASE_DIR) / self.file_name

    def read_json_data(self, path):
        with open(path, encoding='utf-8') as json_file:
            return json.load(json_file)

    def insert_ingredients(self, ingredients):
        added_count = 0
        for entry in ingredients:
            name = entry.get('name', '').strip()
            unit = entry.get('measurement_unit', '').strip()
            if name and unit:
                _, created = Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=unit
                )
                if created:
                    added_count += 1
        return added_count

    def report_file_missing(self, path):
        self.stderr.write(f'Файл не найден: {path}')
