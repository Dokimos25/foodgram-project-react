# Generated by Django 4.2.6 on 2023-10-25 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_ingredientinrecipe_alter_tag_color_recipe_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Время приготовления'),
        ),
    ]