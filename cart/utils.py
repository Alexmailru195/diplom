from django.contrib.auth import get_user
from cart.models import CartItem, GuestCart, Cart


def get_cart_items(request):
    """
    Возвращает список товаров в корзине:
    - Если пользователь аутентифицирован — товары из его корзины.
    - Если гость — товары из гостевой корзины по session_key.
    """
    if request.user.is_authenticated:
        return CartItem.objects.filter(cart__user=request.user).select_related('product')
    else:
        # Получаем ключ сессии, если он ещё не существует — создаём
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        return GuestCart.objects.filter(session_key=session_key).select_related('product')


def merge_guest_cart_to_user_cart(request):
    """
    Объединяет содержимое гостевой корзины (по session_key)
    с корзиной аутентифицированного пользователя.
    """
    user = get_user(request)
    if user.is_authenticated:
        # Получаем или создаём корзину пользователя
        user_cart, created = Cart.objects.get_or_create(user=user)

        # Получаем текущий session_key
        session_key = request.session.session_key

        if session_key and not created:
            # Забираем товары из гостевой корзины
            guest_items = GuestCart.objects.filter(session_key=session_key)

            for item in guest_items:
                # Проверяем, есть ли уже такой товар в корзине пользователя
                cart_item, item_created = CartItem.objects.get_or_create(
                    cart=user_cart,
                    product=item.product,
                    defaults={'quantity': item.quantity}
                )
                if not item_created:
                    # Если товар уже есть — увеличиваем количество
                    cart_item.quantity += item.quantity
                    cart_item.save()

                # Удаляем элемент из гостевой корзины
                item.delete()
