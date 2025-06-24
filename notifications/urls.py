# notifications/urls.py

from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import NotificationViewSet, send_message

router = SimpleRouter()
router.register(r'api/notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    # API маршруты
    path('', include(router.urls)),
    path('send-message/', send_message, name='send_message'),
]
