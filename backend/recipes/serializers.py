from django.core.validators import MinValueValidator
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from ingredients.models import Ingredient
from users.models import User
from users.serializers import PublicUserSerializer

from .models import Recipe, IngredientInRecipe, FavoriteRecipe, ShoppingCart

MIN_INGREDIENT_AMOUNT = 1


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
        return not user.is_anonymous and self._flag_exists(FavoriteRecipe, user, obj)

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return not user.is_anonymous and self._flag_exists(ShoppingCart, user, obj)


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField(validators=[MinValueValidator(MIN_INGREDIENT_AMOUNT)])

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')

    def validate_amount(self, value):
        if value < MIN_INGREDIENT_AMOUNT:
            raise serializers.ValidationError(f'Количество должно быть больше или равно {MIN_INGREDIENT_AMOUNT}.')
        return value


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
            missing = [field for field in ('ingredients', 'image')
                       if field not in data]
            if missing:
                raise serializers.ValidationError({
                    f: 'Обязательное поле.' for f in missing
                })

        image = data.get('image')
        if not image:
            raise serializers.ValidationError(
                {'image': 'Это поле обязательно.'}
            )

        ingredients = data.get('ingredients', [])
        if not ingredients:
            raise serializers.ValidationError(
                'Добавьте хотя бы один ингредиент.'
            )

        seen = set()
        for item in ingredients:
            if item['id'] in seen:
                raise serializers.ValidationError(
                    'Ингредиенты не должны повторяться.'
                )

            ingredient = Ingredient.objects.filter(id=item['id']).first()
            if not ingredient:
                raise serializers.ValidationError(
                    f"Ингредиент с id {item['id']} не существует."
                )

            seen.add(item['id'])

        return data

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
            IngredientInRecipe.objects.filter(recipe=instance).delete()
            self._bulk_create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, recipe):
        return RecipeListSerializer(recipe, context=self.context).data


class ShortLinkSerializer(serializers.Serializer):
    short_link = serializers.SerializerMethodField()

    class Meta:
        fields = ('short_link',)

    def get_short_link(self, obj):
        url = self.context['request'].build_absolute_uri('/')
        return f"{url.rstrip('/')}/recipes/{obj.id}"

    def to_representation(self, instance):
        return {'short-link': self.get_short_link(instance)}


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
