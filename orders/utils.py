# orders/utils.py

from django.db import transaction

from cart.models import Cart
from .models import Order, OrderItem


def create_order_for_user(user, delivery_type, payment_type, address=None):
    """
    Создаёт заказ на основе корзины пользователя.
    Используется как в шаблонных представлениях, так и в API.
    """

    try:
        cart = Cart.objects.get(user=user)
    except Cart.DoesNotExist:
        return None, "Корзина не найдена"

    if not cart.items.exists():
        return None, "Корзина пуста"

    # Рассчитываем общую сумму
    total_price = sum(item.total_price for item in cart.items.all())

    with transaction.atomic():
        order = Order.objects.create(
            user=user,
            delivery_type=delivery_type,
            payment_type=payment_type,
            address=address or '',
            total_price=total_price
        )

        # Переносим товары из корзины в заказ
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )

        # Очищаем корзину
        cart.items.all().delete()

    return order, None