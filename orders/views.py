# orders/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from shop_project import settings
from .models import Order, OrderItem
from cart.models import CartItem
from .forms import OrderConfirmForm

from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_date, parse_time
from django.http import Http404
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


@login_required(login_url='users:login')
def order_confirm_view(request):
    """
    Подтверждение заказа перед оформлением
    """

    if request.user.is_authenticated:
        try:
            cart_items = CartItem.objects.filter(cart__user=request.user)
        except Exception:
            cart_items = []
    else:
        from cart.models import GuestCart
        session_key = request.session.session_key or ''
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart_items = GuestCart.objects.filter(session_key=session_key)

    if not cart_items.exists():
        return redirect('cart:cart_view')

    total_price = sum(item.total for item in cart_items)

    if request.method == 'POST':
        form = OrderConfirmForm(request.POST)
        if form.is_valid():
            delivery_type = form.cleaned_data.get('delivery_type', '')

            order = form.save(commit=False)
            order.user = request.user
            order.total_price = total_price

            # Обработка полей доставки
            if delivery_type == 'courier':
                delivery_date_str = request.POST.get('delivery_date', '').strip()
                delivery_time_str = request.POST.get('delivery_time', '').strip()

                try:
                    delivery_date = parse_date(delivery_date_str) if delivery_date_str else None
                    delivery_time = parse_time(delivery_time_str) if delivery_time_str else None

                    if delivery_date_str and not delivery_date:
                        raise ValueError("Неверный формат даты")
                    if delivery_time_str and not delivery_time:
                        raise ValueError("Неверный формат времени")

                    order.delivery_date = delivery_date
                    order.delivery_time = delivery_time
                    order.pickup_point = None

                except ValueError as e:
                    form.add_error(None, f"Ошибка ввода даты или времени: {e}")
                    return render(request, 'orders/order_confirm.html', {
                        'form': form,
                        'cart_items': cart_items,
                        'total_price': total_price,
                        'pickup_points': Order.PICKUP_POINTS,
                    })

            elif delivery_type == 'pickup':
                pickup_point = request.POST.get('pickup_point', '')
                if not pickup_point:
                    form.add_error(None, "Выберите пункт самовывоза")
                    return render(request, 'orders/order_confirm.html', {
                        'form': form,
                        'cart_items': cart_items,
                        'total_price': total_price,
                        'pickup_points': Order.PICKUP_POINTS,
                    })
                order.pickup_point = pickup_point
                order.delivery_date = None
                order.delivery_time = None

            else:
                form.add_error(None, "Неизвестный способ доставки")
                return render(request, 'orders/order_confirm.html', {
                    'form': form,
                    'cart_items': cart_items,
                    'total_price': total_price,
                    'pickup_points': Order.PICKUP_POINTS,
                })

            order.save()

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )

            # Очистка корзины
            if request.user.is_authenticated:
                cart_items.delete()
            else:
                from cart.models import GuestCart
                GuestCart.objects.filter(session_key=session_key).delete()

            # Отправка email
            subject = 'Ваш заказ оформлен!'
            to_email = order.get_email()
            html_message = render_to_string('orders/order_confirmation_email.html', {
                'order': order,
                'order_items': order.items.all()
            })
            plain_message = strip_tags(html_message)
            try:
                send_mail(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [to_email],
                    html_message=html_message,
                    fail_silently=False
                )
            except Exception as e:
                print(f"Ошибка отправки email: {e}")
                from django.contrib import messages
                messages.warning(request, "Заказ оформлен, но не удалось отправить email")
            return redirect('orders:order_detail', order_id=order.id)

    else:
        form = OrderConfirmForm()

    return render(request, 'orders/order_confirm.html', {
        'form': form,
        'cart_items': cart_items,
        'total_price': total_price,
        'pickup_points': Order.PICKUP_POINTS,
    })


@login_required(login_url='users:login')
def order_list_view(request):
    """
    Список заказов пользователя
    """
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required(login_url='users:login')
def order_detail_view(request, order_id):
    """
    Детали конкретного заказа
    """
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        raise Http404("Заказ не найден или доступ запрещён")

    return render(request, 'orders/order_detail.html', {
        'order': order,
        'order_items': order.items.all(),
    })
