# orders/urls.py

from django.urls import path
from .views import order_confirm_view, order_list_view, order_detail_view

app_name = 'orders'

urlpatterns = [
    path('checkout/', order_confirm_view, name='checkout'),
    path('', order_list_view, name='order_list'),
    path('<int:order_id>/', order_detail_view, name='order_detail'),
]