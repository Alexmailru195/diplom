# products/urls.py

from django.urls import path
from rest_framework.routers import SimpleRouter

from products import views
from products.api_views import CategoryListView, CategoryProductListView, ProductAttributeListView, \
    ProductAttributeValueListView
from products.views import product_detail_view
from .views import product_list_view


# === Роутер для ViewSet (опционально) ===
router = SimpleRouter()


app_name = 'products'


urlpatterns = [
    # === Товары ===
    path('', product_list_view, name='product_list'),
    path('<int:pk>/', product_detail_view, name='product_detail'),

    # === Категории ===
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/<int:category_pk>/products/', CategoryProductListView.as_view(), name='category_products'),

    # === Атрибуты ===
    path('attributes/', ProductAttributeListView.as_view(), name='product_attributes'),
    path('products/<int:product_pk>/attributes/', ProductAttributeValueListView.as_view(),
         name='product_attribute_values'),
]
