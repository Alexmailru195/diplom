# cart/views.py

from django.shortcuts import render
from .models import Cart, CartItem, GuestCart
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from products.models import Product


def cart_view(request):
    if not request.user.is_authenticated:
        return render(request, 'cart/guest_cart.html')  # или редирект на вход

    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()
        total_price = sum(item.total for item in cart_items)
    except Cart.DoesNotExist:
        cart_items = []
        total_price = 0

    return render(request, 'cart/cart_view.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Получаем количество из формы
    quantity_str = request.POST.get('quantity', '1')
    try:
        quantity = int(quantity_str)
        if quantity < 1:
            quantity = 1
    except ValueError:
        quantity = 1

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)

        # Получаем или создаём товар в корзине
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        # Возвращаем пользователя обратно туда, где он был
        return redirect(request.META.get('HTTP_REFERER', 'products:product_list'))

    else:
        session_key = request.session.session_key or ''
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        guest_cart, created = GuestCart.objects.get_or_create(
            session_key=session_key,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            guest_cart.quantity += quantity
            guest_cart.save()

    return redirect('products:product_detail', pk=product_id)


def remove_from_cart(request, product_id):
    if request.user.is_authenticated:
        cart = Cart.objects.get(user=request.user)
        cart.items.filter(product_id=product_id).delete()
    else:
        session_key = request.session.session_key or ''
        from .models import GuestCart
        GuestCart.objects.filter(session_key=session_key, product_id=product_id).delete()

    return redirect('cart:cart_view')


@login_required(login_url='users:login')
def update_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity_str = request.POST.get('quantity', '1')

        if not product_id:
            return redirect('cart:cart_view')

        # Проверка корректности значения quantity
        try:
            quantity = int(quantity_str)
            if quantity < 1:
                quantity = 1
        except (ValueError, TypeError):
            quantity = 1

        if request.user.is_authenticated:
            try:
                cart_item = CartItem.objects.get(cart__user=request.user, product_id=product_id)
                cart_item.quantity = quantity
                cart_item.save()
            except CartItem.DoesNotExist:
                pass
        else:
            from django.contrib.sessions.backends.db import SessionStore
            session_key = request.session.session_key or ''
            if not session_key:
                request.session.save()
                session_key = request.session.session_key

            guest_cart, created = GuestCart.objects.get_or_create(
                session_key=session_key,
                product_id=product_id,
                defaults={'quantity': quantity}
            )
            if not created:
                guest_cart.quantity = quantity
                guest_cart.save()

        return redirect('cart:cart_view')

    return redirect('cart:cart_view')