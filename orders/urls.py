# orders/urls.py

from django.urls import path

from . import views
from .views import (
    order_confirm_view,
    order_list_view,
    user_orders_view,
    order_detail_view,
    update_order_status,
    profile_orders_view
)


app_name = 'orders'

urlpatterns = [
    path('checkout/', order_confirm_view, name='checkout'),
    path('', order_list_view, name='order_list'),
    path('user/', user_orders_view, name='user_orders'),
    path('<int:order_id>/', order_detail_view, name='order_detail'),
    path('<int:order_id>/update-status/', update_order_status, name='update_order_status'),
    path('profile/', profile_orders_view, name='profile_orders'),
    path('<int:order_id>/confirm-payment/', views.payment_confirmation, name='payment_confirmation'),
    path('<int:order_id>/pay/', views.payment_process, name='payment_process'),
]
