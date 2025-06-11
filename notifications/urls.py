# notifications/urls.py

from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import NotificationViewSet


router = SimpleRouter()
router.register(r'api/notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    # API маршруты
    path('', include(router.urls)),
]