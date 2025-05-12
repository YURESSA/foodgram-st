from django.contrib import admin

from .models import (Recipe, IngredientInRecipe, FavoriteRecipe,
                     ShoppingCart)


class IngredientInRecipeInline(admin.TabularInline):
    model = IngredientInRecipe
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'cooking_time',
                    'created_at', 'image_tag')
    search_fields = ('name', 'author__username', 'author__email')
    list_filter = ('author', 'created_at')
    ordering = ('-created_at',)
    inlines = [IngredientInRecipeInline]


@admin.register(IngredientInRecipe)
class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount', 'created_at')
    search_fields = ('recipe__name', 'ingredient__name')
    list_filter = ('ingredient',)
    ordering = ('-created_at',)


@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'added_at')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('added_at',)
    ordering = ('-added_at',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'added_at')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('added_at',)
    ordering = ('-added_at',)
