from django.db import models


class Recipe(models.Model):
    name = models.CharField('Название', max_length=100)
    category = models.CharField('Категория', max_length=50)
    cook_time = models.PositiveIntegerField('Время приготовления (мин)')
    servings = models.PositiveIntegerField('Количество порций')
    ingredients = models.TextField('Ингредиенты', max_length=1000)
    instructions = models.TextField('Способ приготовления', max_length=3000)

    def __str__(self):
        return self.name
