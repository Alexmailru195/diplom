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

    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = cart.items.get_or_create(product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        return redirect('products:product_detail', pk=product_id)
    else:
        # Обработка гостевой корзины через сессию или GuestCart
        session_key = request.session.session_key or ''
        from .models import GuestCart
        guest_cart, created = GuestCart.objects.get_or_create(
            session_key=session_key,
            product=product
        )
        if not created:
            guest_cart.quantity += 1
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


def update_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))

        if request.user.is_authenticated:
            cart = Cart.objects.get(user=request.user)
            cart_item = cart.items.get(product_id=product_id)
            cart_item.quantity = quantity
            cart_item.save()
        else:
            session_key = request.session.session_key or ''
            guest_cart = GuestCart.objects.get(session_key=session_key, product_id=product_id)
            guest_cart.quantity = quantity
            guest_cart.save()

    return redirect('cart:cart_view')