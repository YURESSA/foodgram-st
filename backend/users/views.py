from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Follow
from .pagination import UserPagination
from .serializers import (
    PublicUserSerializer, SetAvatarSerializer, UserWithRecipesSerializer
)

User = get_user_model()


class ExtendedUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = PublicUserSerializer
    pagination_class = UserPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def update_avatar(self, user, data, request):
        if 'avatar' not in data:
            return Response(
                {'detail': 'Поле avatar обязательно для заполнения.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SetAvatarSerializer(
            user, data=data, partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            try:
                serializer.save()
                avatar_url = request.build_absolute_uri(
                    user.profile_image.url
                ) if user.profile_image else None
                return Response(
                    {'avatar': avatar_url},
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                return Response(
                    {'detail': f'Error saving avatar: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete_avatar(self, user):
        try:
            if user.profile_image:
                user.profile_image.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response(
                {'detail': f'Error deleting avatar: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False,
            methods=['get'],
            permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        user_serializer = PublicUserSerializer(request.user)
        return Response(user_serializer.data)

    @action(
        detail=False,
        methods=['put', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='me/avatar',
        url_name='user_avatar'
    )
    def manage_profile_image(self, request):
        user = request.user

        if request.method == 'PUT':
            return self.update_avatar(user, request.data, request)

        if request.method == 'DELETE':
            return self.delete_avatar(user)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(follower_set__follower=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserWithRecipesSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = UserWithRecipesSerializer(
            queryset, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='subscribe'
    )
    def subscribe(self, request, **kwargs):
        author_id = kwargs.get('id') or kwargs.get('pk')
        author = get_object_or_404(User, id=author_id)

        if request.user == author:
            return Response(
                {'detail': 'Нельзя подписаться на самого себя!'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == 'POST':
            if Follow.objects.filter(
                    follower=request.user,
                    following=author
            ).exists():
                return Response(
                    {'detail': 'Вы уже подписаны на этого автора!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Follow.objects.create(follower=request.user, following=author)

            serializer = UserWithRecipesSerializer(
                author,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        follow = Follow.objects.filter(follower=request.user, following=author)
        if not follow.exists():
            return Response(
                {'detail': 'Вы не подписаны на этого автора!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
