from io import BytesIO

from api.filters import RecipeFilter
from api.permissions import OwnershipPermission
from api.serializers import (
    IngredientSerializer,
    CreateRecipeSerializer,
    RecipeSerializer,
    FavoriteSerializer,
    CartSerializer
)
from django.db.models import Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from recipe.models import Ingredient, Recipe, UserCart
from rest_framework import (
    decorators,
    filters,
    permissions,
    response,
    status,
    viewsets
)


class IngredientViewset(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("^name",)
    permission_classes = (permissions.AllowAny,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (OwnershipPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ("create", "partial_update"):
            return CreateRecipeSerializer
        return RecipeSerializer

    @decorators.action(
        detail=True,
        methods=("post", "delete"),
        url_path="favorite",
        permission_classes=(permissions.IsAuthenticated,)
    )
    def favorite(self, request, pk):
        return self._handle_recipe_action(request, pk, FavoriteSerializer)

    @decorators.action(
        detail=True,
        methods=("post", "delete"),
        url_path="shopping_cart",
        permission_classes=(permissions.IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return self._handle_recipe_action(request, pk, CartSerializer)

    def _handle_recipe_action(self, request, pk, serializer_class):
        self._get_recipe_or_404(pk)

        if request.method == "POST":
            serializer = serializer_class(
                data={"user": request.user.id, "recipe": pk}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)

        model = serializer_class.Meta.model
        obj = model.objects.filter(user=request.user, recipe_id=pk)
        if obj.exists():
            obj.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        return response.Response(status=status.HTTP_400_BAD_REQUEST)

    @decorators.action(
        detail=False,
        methods=("get",),
        url_path="download_shopping_cart",
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients = UserCart.objects.filter(user=request.user).values(
            "recipe__ingredients_in_recipe__ingredient__name",
            "recipe__ingredients_in_recipe__ingredient__measurement_unit"
        ).annotate(
            total=Sum("recipe__ingredients_in_recipe__amount")
        )
        return self._ingredients_to_txt(ingredients)

    def _ingredients_to_txt(self, ingredients):
        lines = [
            f"{item['recipe__ingredients_in_recipe__ingredient__name']} - "
            f"{item['total']} ("
            f"{item['recipe__ingredients_in_recipe__ingredient__measurement_unit']})"
            for item in ingredients
        ]
        content = "\n".join(lines)
        file = BytesIO()
        file.write(content.encode())
        file.seek(0)

        return FileResponse(
            file,
            as_attachment=True,
            filename="Список покупок.txt",
            content_type="text/plain"
        )

    @decorators.action(
        detail=True,
        methods=("get",),
        url_path="get-link",
        url_name="get-link"
    )
    def get_short_link(self, request, pk):
        recipe = self.get_object()
        url = f"{request.get_host()}/s/{recipe.pk}"
        return response.Response(data={"short-link": url})

    def _get_recipe_or_404(self, pk):
        return get_object_or_404(Recipe, pk=pk)
