# orders/urls.py

from django.urls import path
from . import views
from .views import order_confirm_view

app_name = 'orders'

urlpatterns = [
    # Список заказов пользователя
    path('', views.order_list_view, name='order_list'),

    # Подтверждение заказа (форма доставки)
    path('checkout/', order_confirm_view, name='create_order'),

    # Детали конкретного заказа
    path('<int:order_id>/', views.order_detail_view, name='order_detail'),
]