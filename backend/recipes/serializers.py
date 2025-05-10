from api.serializers import RecipeMinifiedSerializer
from drf_extra_fields.fields import Base64ImageField
from ingredients.models import Ingredient
from rest_framework import serializers
from users.models import User
from users.serializers import PublicUserSerializer

from .models import (
    Recipe, IngredientInRecipe,
    FavoriteRecipe, ShoppingCart
)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeListSerializer(serializers.ModelSerializer):
    author = PublicUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='ingredients_in_recipe', many=True, read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text',
            'cooking_time',
        )

    def get_image(self, obj):
        if not obj.image:
            return ''
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image.url)

    def _flag_exists(self, model, user, recipe):
        return model.objects.filter(user=user, recipe=recipe).exists()

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return False if user.is_anonymous else self._flag_exists(
            FavoriteRecipe, user, obj
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return False if user.is_anonymous else self._flag_exists(
            ShoppingCart, user, obj
        )


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    author = PublicUserSerializer(read_only=True)
    ingredients = AddIngredientSerializer(many=True)
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'image',
            'name', 'text', 'cooking_time',
        )

    def validate(self, data):
        request = self.context.get('request')
        if request and request.method in ('PUT', 'PATCH'):
            missing = []
            for field in ('ingredients', 'image'):
                if field not in data:
                    missing.append(field)
            if missing:
                raise serializers.ValidationError({
                    f: 'Обязательное поле.' for f in missing
                })
        return data

    def validate_image(self, file):
        if not file:
            raise serializers.ValidationError(
                'Поле image не может быть пустым.'
            )
        return file

    def validate_ingredients(self, items):
        if not items:
            raise serializers.ValidationError(
                'Добавьте хотя бы один ингредиент.'
            )
        seen = set()
        for item in items:
            ing = Ingredient.objects.filter(id=item['id']).first()
            if not ing:
                raise serializers.ValidationError(
                    f'Ингредиент #{item["id"]} не найден.'
                )
            if item['id'] in seen:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться.'
                )
            if item['amount'] < 1:
                raise serializers.ValidationError(
                    'Количество должно быть > 0.'
                )
            seen.add(item['id'])
        return items

    def _bulk_create_ingredients(self, recipe, ingredients):
        objs = [
            IngredientInRecipe(
                recipe=recipe,
                ingredient_id=item['id'],
                amount=item['amount']
            ) for item in ingredients
        ]
        IngredientInRecipe.objects.bulk_create(objs)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        author = self.context['request'].user
        recipe = Recipe.objects.create(author=author, **validated_data)
        self._bulk_create_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self._bulk_create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, recipe):
        return RecipeListSerializer(recipe, context=self.context).data


class ShortLinkSerializer(serializers.Serializer):
    short_link = serializers.SerializerMethodField()

    class Meta:
        fields = ('short-link',)

    def get_short_link(self, obj):
        url = self.context['request'].build_absolute_uri('/')
        return f"{url.rstrip('/')}/api/recipes/{obj.id}"

    def to_representation(self, instance):
        return {'short-link': self.get_short_link(instance)}


class UserWithRecipesSerializer(serializers.ModelSerializer):
    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name',
                  'recipes_count', 'recipes')

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_qs = obj.recipes.all()
        limit = request.query_params.get('recipes_limit')
        if limit:
            try:
                limit = int(limit)
                recipes_qs = recipes_qs[:limit]
            except ValueError:
                pass
        serializer = RecipeMinifiedSerializer(
            recipes_qs,
            many=True,
            context={'request': request}
        )
        return serializer.data
