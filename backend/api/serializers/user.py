from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from django.contrib.auth import get_user_model
from auth_user.models import Subscribe

User = get_user_model()


class IsSubscribedMixin(serializers.Serializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        user = self.context.get("request").user
        return user.is_authenticated and user.subscriptions.filter(
            target=obj.id
        ).exists()


class AuthorSerializer(UserSerializer, IsSubscribedMixin):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = (
            "id", "email", "username", "first_name",
            "last_name", "avatar", "is_subscribed"
        )


class CreateAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ("avatar",)


class CreateUser(UserCreateSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = (
            "email", "id", "username",
            "first_name", "last_name", "password"
        )
