from rest_framework import serializers

from recipe.models import UserCart, UserFavorite
from .recipe import ShortRecipeSerializer


class RecipeCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        abstract = True
        fields = ("user", "recipe")

    def to_representation(self, instance):
        return ShortRecipeSerializer(
            instance.recipe,
            context=self.context
        ).data

    def validate(self, attrs):
        user = attrs["user"]
        recipe = attrs["recipe"]
        if self.Meta.model.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError("Запись уже существует")
        return attrs


class FavoriteSerializer(RecipeCollectionSerializer):
    class Meta(RecipeCollectionSerializer.Meta):
        model = UserFavorite


class CartSerializer(RecipeCollectionSerializer):
    class Meta(RecipeCollectionSerializer.Meta):
        model = UserCart
