from django.db import models

INGREDIENT_NAME_MAX_LENGTH = 128
UNIT_MAX_LENGTH = 64


class Ingredient(models.Model):
    name = models.CharField(
        max_length=INGREDIENT_NAME_MAX_LENGTH,
        verbose_name='Ингредиент'
    )
    measurement_unit = models.CharField(
        max_length=UNIT_MAX_LENGTH,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Список ингредиентов'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='ingredient_unique_name_unit'
            )
        ]

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'
