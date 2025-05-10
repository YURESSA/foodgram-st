from django.db import models


class Ingredient(models.Model):
    name = models.CharField(
        max_length=128,
        verbose_name='Ингредиент'
    )
    measurement_unit = models.CharField(
        max_length=64,
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
