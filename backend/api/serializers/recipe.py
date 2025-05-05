from drf_extra_fields.fields import Base64ImageField
from recipe.models import Recipe, IngredientInRecipe
from rest_framework import serializers

from .ingredient import IngredientRecipeSerializer, CreateIngredientSerializer
from .user import AuthorSerializer


class ShortRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class RecipeSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    ingredients = IngredientRecipeSerializer(
        many=True,
        source="ingredients_in_recipe"
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id", "author", "ingredients", "is_favorited",
            "is_in_shopping_cart", "name", "image", "text", "cooking_time"
        )

    def get_is_favorited(self, obj):
        user = self.context.get("request").user
        return user.is_authenticated and user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get("request").user
        return user.is_authenticated and user.carts.filter(recipe=obj).exists()


class CreateRecipeSerializer(serializers.ModelSerializer):
    ingredients = CreateIngredientSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("ingredients", "name", "image", "text", "cooking_time")

    def validate(self, data):
        ingredients = data.get("ingredients")
        if not ingredients:
            raise serializers.ValidationError({"ingredients": "Обязательное поле"})
        ids = [i["id"] for i in ingredients]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError({"ingredients": "Ингредиенты не должны повторяться"})
        return data

    def validate_image(self, value):
        if not value:
            raise serializers.ValidationError({"image": "Обязательное поле"})
        return value

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        user = self.context["request"].user
        recipe = Recipe.objects.create(author=user, **validated_data)
        self._add_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop("ingredients")
        IngredientInRecipe.objects.filter(recipe=instance).delete()
        self._add_ingredients(ingredients, instance)
        return super().update(instance, validated_data)

    def _add_ingredients(self, ingredients, recipe):
        IngredientInRecipe.objects.bulk_create([
            IngredientInRecipe(
                recipe=recipe,
                ingredient_id=ingredient["id"],
                amount=ingredient["amount"]
            ) for ingredient in ingredients
        ])

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data
