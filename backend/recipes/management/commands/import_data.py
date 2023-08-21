import csv
import os

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    file_path = os.path.join('data', 'ingredients.csv')

    def handle(self, *args, **options):
        try:
            self._load_data()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при импорте {e}'))
        else:
            self.stdout.write(self.style.SUCCESS('Данные загружены успешно!'))

    def _load_data(self):
        with open(self.file_path, encoding='UTF-8') as f:
            read_data = csv.reader(f)
            next(read_data)
            items = [
                Ingredient(name=name, measurement_unit=unit)
                for name, unit in read_data
            ]
            Ingredient.objects.bulk_create(items)
