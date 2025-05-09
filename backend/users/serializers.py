from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

User = get_user_model()


class RegisterUserSerializer(UserCreateSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name', 'password'
        )


class PublicUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name',
            'is_subscribed', 'profile_image'
        )

    def get_profile_image(self, obj):
        image = getattr(obj, 'profile_image', None)
        if image:
            request = self.context.get('request')
            return request.build_absolute_uri(image.url) if request else image.url
        return None
