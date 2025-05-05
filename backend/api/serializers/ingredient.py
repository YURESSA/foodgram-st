from foodgram import constants
from recipe.models import Ingredient, IngredientInRecipe
from rest_framework import serializers


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")
        read_only_fields = ("id", "name", "measurement_unit")


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class CreateIngredientSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        fields = ("id", "amount")

    def validate_id(self, value):
        if not Ingredient.objects.filter(pk=value).exists():
            raise serializers.ValidationError(
                {"id": "Недействительный идентификатор"}
            )
        return value

    def validate_amount(self, value):
        if value < constants.MIN_INGREDIENT_AMOUNT:
            raise serializers.ValidationError(
                {"amount": "Недопустимое значение"}
            )
        return value
