# cart/urls.py

from django.urls import path, include
from rest_framework.routers import SimpleRouter
from cart.api_views import CartViewSet
from .views import cart_view, add_to_cart, remove_from_cart, update_cart, update_cart_ajax, remove_from_cart_ajax

router = SimpleRouter()
router.register(r'api/cart', CartViewSet, basename='cart_api')

app_name = 'cart'

urlpatterns = [
    path('', cart_view, name='cart_view'),
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('update/', update_cart, name='update_cart'),
    path('update-ajax/', update_cart_ajax, name='update_cart_ajax'),
    path('remove-ajax/<int:product_id>/', remove_from_cart_ajax, name='remove_from_cart_ajax'),

    path('api/', include(router.urls)),
]