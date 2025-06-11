from django.urls import path
from .views import CartViewSet, OrderViewSet
from rest_framework.routers import SimpleRouter


router = SimpleRouter()
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'orders', OrderViewSet, basename='orders')

urlpatterns = router.urls
