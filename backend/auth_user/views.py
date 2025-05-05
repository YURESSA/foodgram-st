from api.filters import RecipeFilter
from api.permissions import OwnershipPermission
from api.serializers import (
    RecipeSerializer, CreateRecipeSerializer, FavoriteSerializer, CartSerializer,
    SubscriptionSerializer, SubscriberSerializer, CreateAvatarSerializer
)
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser import views
from recipe.models import Recipe, UserCart
from rest_framework import decorators, response, status, permissions


class UserViewSet(views.UserViewSet):
    queryset = get_user_model().objects.all()
    permission_classes = (OwnershipPermission,)

    @decorators.action(
        detail=True,
        methods=["put", "delete"],
        url_path="avatar",
        permission_classes=[permissions.IsAuthenticated],
    )
    def avatar(self, request, id):
        if request.method == "PUT":
            return self._create_avatar(request)
        return self._delete_avatar(request)

    def _create_avatar(self, request):
        serializer = CreateAvatarSerializer(
            request.user, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data)

    def _delete_avatar(self, request):
        user = request.user
        if user.avatar:
            user.avatar.delete()
            user.avatar = None
            user.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @decorators.action(
        detail=False,
        methods=["get"],
        url_path="subscriptions",
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscriptions(self, request):
        target_ids = request.user.subscriptions.values_list("target", flat=True)
        queryset = self.get_queryset().filter(pk__in=target_ids)
        page = self.paginate_queryset(queryset)
        serializer = SubscriberSerializer(page, many=True, context={"request": request})
        return self.get_paginated_response(serializer.data)

    @decorators.action(
        detail=True,
        methods=["post", "delete"],
        url_path="subscribe",
        permission_classes=[permissions.IsAuthenticated],
    )
    def subscribe(self, request, id):
        user_model = get_user_model()
        get_object_or_404(user_model, pk=id)

        if request.method == "POST":
            return self._create_subscription(request, id)
        return self._delete_subscription(request, id)

    def _create_subscription(self, request, pk):
        if request.user.pk == int(pk):
            return response.Response(status=status.HTTP_400_BAD_REQUEST)

        serializer = SubscriptionSerializer(
            data={"subscribing_user": request.user.pk, "target": pk},
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        response_serializer = SubscriberSerializer(
            self.get_queryset().get(pk=pk), context={"request": request}
        )
        return response.Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def _delete_subscription(self, request, pk):
        model = SubscriptionSerializer.Meta.model
        subscription = model.objects.filter(
            subscribing_user=request.user, target_id=pk
        )
        if subscription.exists():
            subscription.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        return response.Response(status=status.HTTP_400_BAD_REQUEST)
