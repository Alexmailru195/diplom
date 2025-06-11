# inventory/urls.py

from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import InventoryViewSet

router = SimpleRouter()
router.register(r'api/inventory', InventoryViewSet, basename='inventory')

urlpatterns = [
    # API маршруты для инвентаря
    path('', include(router.urls)),
]