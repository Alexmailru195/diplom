# pos/urls.py

from django.urls import path
from . import views
from inventory.views import move_inventory as move_inventory_view
from .views import edit_point_view

app_name = 'pos'

urlpatterns = [
    path('', views.point_list_view, name='point_list'),
    path('<int:point_id>/', views.point_detail_view, name='point_detail'),
    path('move/', move_inventory_view, name='move_inventory'),
    path('add/', views.point_create_view, name='point_add'),
    path('<int:point_id>/edit/', views.point_update_view, name='point_edit'),
    path('<int:point_id>/delete/', views.point_delete_view, name='point_delete'),
    path('<int:point_id>/edit/', edit_point_view, name='edit_point'),
]
