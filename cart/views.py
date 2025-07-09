# cart/views.py
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from products.models import Product
from .models import Cart, CartItem, GuestCart


def cart_view(request):
    """
    Отображает корзину пользователя.
    Если пользователь неавторизован — отображает гостевую корзину.
    """

    if not request.user.is_authenticated:
        return render(request, 'cart/guest_cart.html')

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
    """
    Добавляет товар в корзину.

    Args:
        product_id (int): ID товара, который нужно добавить.

    Returns:
        redirect: Возвращает на предыдущую страницу или на детали товара.
    """

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
    """
    Удаляет товар из корзины.

    Args:
        product_id (int): ID товара, который нужно удалить.

    Returns:
        redirect: Возвращает на страницу корзины.
    """

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
    """
    Обновляет количество товара в корзине после POST-запроса.

    Args:
        product_id (str): ID товара.
        quantity (str): Новое количество товара.

    Returns:
        redirect: Возвращает на страницу корзины.
    """

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


@csrf_exempt
def update_cart_ajax(request):
    """
    AJAX-метод для обновления количества товара в корзине.

    Args:
        quantity (str): Новое количество товара.
        cart_item_id (str): ID позиции в корзине.

    Returns:
        JsonResponse: Содержит обновлённые данные о корзине.
    """

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity'))
        cart_item_id = request.POST.get('cart_item_id')

        try:
            item = CartItem.objects.get(id=cart_item_id)
        except CartItem.DoesNotExist:
            return JsonResponse({'error': 'Позиция не найдена'}, status=400)

        # Дополнительные проверки можно добавить здесь
        item.quantity = quantity
        item.save()

        return JsonResponse({
            'total_price': item.cart.total_price,
            'total_line_price': item.total,
            'message': 'Количество обновлено'
        })


@csrf_exempt
def remove_from_cart_ajax(request, product_id=None):
    """
    AJAX-метод для удаления товара из корзины.

    Args:
        product_id (int): ID товара, который нужно удалить.

    Returns:
        JsonResponse: Содержит информацию об успешном удалении.
    """

    if request.method == 'POST':
        # Получаем product_id из POST данных, если он не передан через URL
        product_id = product_id or request.POST.get('product_id')

        try:
            item = CartItem.objects.get(product__id=product_id)
            item.delete()
        except CartItem.DoesNotExist:
            return JsonResponse({'error': 'Позиция не найдена'}, status=400)

        return JsonResponse({
            'total_price': item.cart.total_price,
            'message': 'Товар успешно удалён'
        })


def get_cart_items(request):
    """
    Вспомогательная функция для получения товаров в корзине.
    Используется для шаблонов и API.

    Returns:
        QuerySet: Товары в корзине (CartItem или GuestCart).
    """

    if request.user.is_authenticated:
        return CartItem.objects.filter(cart__user=request.user).select_related('product')
    else:
        session_key = request.session.session_key or ''
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        return GuestCart.objects.filter(session_key=session_key).select_related('product')


@login_required
def merge_guest_cart(request):
    """
    Переносит товары из гостевой корзины в обычную при входе пользователя.
    """

    # Получаем ключ текущей сессии
    session_key = request.session.session_key or ''
    if not session_key:
        return redirect('cart:cart_view')

    # Получаем или создаём корзину пользователя
    try:
        cart = request.user.cart
    except Cart.DoesNotExist:
        cart = Cart.objects.create(user=request.user)

    # Переносим товары из гостевой корзины
    guest_items = GuestCart.objects.filter(session_key=session_key)
    for item in guest_items:
        product = item.product
        quantity = item.quantity

        # Получаем или создаём позицию в пользовательской корзине
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        else:
            cart_item.save()

    # Очищаем гостевую корзину
    guest_items.delete()

    return redirect('cart:cart_view')
