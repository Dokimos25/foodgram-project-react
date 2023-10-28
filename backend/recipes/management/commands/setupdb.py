import json

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка ингредиентов из json-файла'

    def handle(self, *args, **kwargs):
        with open('../data/ingredients.json', encoding='utf-8') as file:
            data = json.load(file)
            for ingredient in data:
                Ingredient.objects.get_or_create(
                    name=ingredient['name'],
                    measurement_unit=ingredient['measurement_unit'],
                )
                self.stdout.write(
                    "Ингредиент {} добавлен".format(ingredient['name'])
                )
        self.stdout.write(self.style.SUCCESS('Данные ингредиентов загружены.'))
