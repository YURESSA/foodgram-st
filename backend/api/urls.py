from django.urls import include, path

from rest_framework.routers import DefaultRouter

from ingredients.views import IngredientCatalogView
from recipes.views import RecipeViewSet
from users.views import ExtendedUserViewSet


router = DefaultRouter()
router.register(r'users', ExtendedUserViewSet, basename='users')
router.register(r'ingredients', IngredientCatalogView, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
