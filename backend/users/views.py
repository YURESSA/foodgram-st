from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import permissions

from .pagination import CustomPagination
from .serializers import (
    PublicUserSerializer
)

User = get_user_model()


class ExtendedUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = PublicUserSerializer
    pagination_class = CustomPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
