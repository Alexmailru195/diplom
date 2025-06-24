# cart/utils.py

from django.contrib.auth import get_user_model

from cart.models import CartItem, GuestCart, Cart

User = get_user_model()


def get_cart_items(request):
    if request.user.is_authenticated:
        return CartItem.objects.filter(cart__user=request.user).select_related('product')
    else:
        session_key = request.session.session_key or ''
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        return GuestCart.objects.filter(session_key=session_key).select_related('product')


def merge_guest_cart_to_user_cart(request):
    if request.user.is_authenticated:
        user_cart, created = Cart.objects.get_or_create(user=request.user)
        session_key = request.session.session_key
        if session_key and not created:
            guest_items = GuestCart.objects.filter(session_key=session_key)
            for item in guest_items:
                # Проверяем, есть ли уже такой товар в корзине пользователя
                cart_item, created = CartItem.objects.get_or_create(
                    cart=user_cart,
                    product=item.product,
                    defaults={'quantity': item.quantity}
                )
                if not created:
                    cart_item.quantity += item.quantity
                    cart_item.save()
                item.delete()  # Удаляем товар из гостевой корзины