from rest_framework.pagination import PageNumberPagination

from constants import USER_PAGE_SIZE


class UserPagination(PageNumberPagination):
    page_size = USER_PAGE_SIZE
    page_size_query_param = 'limit'
