from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import ExtendedUserViewSet

router = DefaultRouter()
router.register(r'users', ExtendedUserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]