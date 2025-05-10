from api.pagination import CustomPagination
from api.serializers import RecipeMinifiedSerializer
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .filters import RecipeFilter
from .models import Recipe, FavoriteRecipe, ShoppingCart, IngredientInRecipe
from .permissions import IsAdminOrAuthorOrReadOnly
from .serializers import (RecipeListSerializer, RecipeCreateUpdateSerializer,
                          ShortLinkSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = CustomPagination
    permission_classes = [IsAdminOrAuthorOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return RecipeCreateUpdateSerializer
        return RecipeListSerializer

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[permissions.AllowAny],
        url_path='get-link',
        url_name='get_link'
    )
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = ShortLinkSerializer(
            recipe, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if FavoriteRecipe.objects.filter(
                    user=request.user, recipe=recipe
            ).exists():
                return Response(
                    {'detail': 'Рецепт уже в избранном!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            FavoriteRecipe.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeMinifiedSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        favorite = FavoriteRecipe.objects.filter(
            user=request.user, recipe=recipe
        )
        if not favorite.exists():
            return Response(
                {'detail': 'Рецепта нет в избранном!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            if (ShoppingCart.objects.filter
                (user=request.user,
                 recipe=recipe
                 ).exists()):
                return Response(
                    {'detail': 'Этот рецепт уже добавлен в вашу корзину!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            ShoppingCart.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeMinifiedSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        cart_item = ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe
        )
        if not cart_item.exists():
            return Response(
                {'detail': 'Этот рецепт отсутствует в вашей корзине!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = IngredientInRecipe.objects.filter(
            recipe__in_shopping_carts__user=request.user
        ).values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(
            total_amount=Sum('amount')
        ).order_by('ingredient__name')

        shopping_list = "Список покупок:\n\n"
        for idx, item in enumerate(ingredients, 1):
            shopping_list += (f"{idx}. {item['ingredient__name']} - "
                              f"{item['total_amount']} "
                              f"{item['ingredient__measurement_unit']}\n")

        response = HttpResponse(
            shopping_list,
            content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = \
            'attachment; filename=shopping_list.txt'

        return response
