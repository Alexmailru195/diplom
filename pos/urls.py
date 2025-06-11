# pos/urls.py
from . import views
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import PosViewSet


# === Роутер для API ===
router = SimpleRouter()
router.register(r'api/pos', PosViewSet, basename='pos_api')

# === Дополнительные маршруты ===
urlpatterns = [
    # Можно добавить шаблоны, если используется интерфейс для продавца
    path('pos/', views.pos_list_view, name='pos_list'),
    path('pos/<int:pk>/', views.pos_detail_view, name='pos_detail'),
]

# === Подключаем маршруты из роутера ===
urlpatterns += router.urls