# inventory/urls.py

from django.urls import path
from . import views
from .views import inventory_list_view, stock_history

app_name = 'inventory'

urlpatterns = [
    path('', inventory_list_view, name='inventory_list'),
    path('<int:inventory_id>/', views.inventory_detail_view, name='inventory_detail'),
    path('add/', views.add_inventory, name='add'),
    path('move/', views.move_inventory, name='move_inventory'),
    path('low-stock/', views.low_stock_alert, name='low_stock_alert'),
    path('history/', stock_history, name='stock_history'),
]
