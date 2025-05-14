from rest_framework.pagination import PageNumberPagination

from constants import RECIPE_PAGE_SIZE


class RecipesPagination(PageNumberPagination):
    page_size = RECIPE_PAGE_SIZE
    page_size_query_param = 'limit'
