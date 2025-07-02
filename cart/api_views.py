# cart/api_views.py

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from products.models import Product
from .models import Cart
from .serializers import CartSerializer, AddToCartSerializer


class CartViewSet(ViewSet):
    def list(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        serializer = AddToCartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data.get('quantity', 1)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'detail': 'Товар не найден'}, status=status.HTTP_404_NOT_FOUND)

        cart, created = Cart.objects.get_or_create(user=request.user)

        cart_item, item_created = cart.items.get_or_create(
            product=product,
            defaults={'quantity': quantity}
        )

        if not item_created:
            cart_item.quantity += quantity
            cart_item.save()

        return Response({
            'detail': 'Товар добавлен в корзину',
            'cart': CartSerializer(cart).data
        })

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'detail': 'Не указан product_id'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart = Cart.objects.get(user=request.user)
            cart.items.filter(product_id=product_id).delete()
            return Response({'detail': 'Товар удален из корзины'})
        except Cart.DoesNotExist:
            return Response({'detail': 'Корзина не найдена'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()
            return Response({'detail': 'Корзина очищена'})
        except Cart.DoesNotExist:
            return Response({'detail': 'Корзина не найдена'}, status=status.HTTP_404_NOT_FOUND)
