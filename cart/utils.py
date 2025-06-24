from cart.models import CartItem, GuestCart


def get_cart_items(request):
    if request.user.is_authenticated:
        return CartItem.objects.filter(cart__user=request.user).select_related('product')
    else:
        session_key = request.session.session_key or ''
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        return GuestCart.objects.filter(session_key=session_key).select_related('product')
