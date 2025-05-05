from auth_user.models import Subscribe
from django.contrib.auth import get_user_model
from rest_framework import serializers

from .recipe import ShortRecipeSerializer
from .user import AuthorSerializer, IsSubscribedMixin

User = get_user_model()


class SubscriberSerializer(AuthorSerializer, IsSubscribedMixin):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source="recipes.count")

    class Meta:
        model = User
        fields = (
            "id", "email", "username", "first_name", "last_name",
            "recipes", "recipes_count", "avatar", "is_subscribed"
        )

    def get_recipes(self, obj):
        queryset = obj.recipes.all()
        limit = self.context["request"].query_params.get("recipes_limit")
        if limit and limit.isdigit():
            queryset = queryset[:int(limit)]
        return ShortRecipeSerializer(queryset, many=True, context=self.context).data


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = ("subscribing_user", "target")
