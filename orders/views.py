# orders/views.py
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.db import transaction
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.utils.html import strip_tags

from cart.models import CartItem
from inventory.models import PointInventory, StockHistory
from orders.utils import send_order_status_email
from pos.models import Point
from . import forms
from .forms import OrderConfirmForm
from .models import Order, OrderItem


@login_required
def update_order_status(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        messages.error(request, "Заказ не найден")
        return redirect('orders:order_detail', order_id=order_id)

    forbidden_statuses = ['cancelled', 'delivered']

    if order.status in forbidden_statuses:
        messages.warning(request, f"Заказ с статусом '{order.get_status_display()}' редактировать нельзя.")
        return redirect('orders:order_detail', order_id=order_id)

    if not request.user.is_superuser and request.user != order.manager and request.user != order.user:
        messages.error(request, "У вас нет прав на изменение этого заказа")
        return redirect('orders:order_detail', order_id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('status')

        valid_statuses = [key for key, _ in Order.STATUS_CHOICES]
        if new_status in valid_statuses:
            old_status = order.status
            order.status = new_status
            order.save()

            # Отправляем уведомление пользователю
            send_order_status_email(order, order.user)  # ← отправляем email пользователю
            messages.success(request, f"Статус заказа изменён на {order.get_status_display()}")
        else:
            messages.error(request, "Неверный статус")

        return redirect('orders:order_detail', order_id=order_id)


@login_required
def order_list_view(request):
    """
    Список всех заказов (для менеджеров и админов)
    """
    if request.user.is_superuser or request.user.is_staff:
        # Администраторы и менеджеры видят все заказы
        status_filter = request.GET.get('status')
        orders = Order.objects.all().order_by('-created_at')

        if status_filter:
            orders = orders.filter(status=status_filter)

        return render(request, 'orders/admin_order_list.html', {
            'orders': orders,
            'STATUS_CHOICES': [choice for choice in Order.STATUS_CHOICES]
        })
    else:
        # Обычные пользователи видят только свои заказы
        return user_orders_view(request)



@login_required
def all_orders_view(request):
    """
    Список всех заказов (для админов и менеджеров)
    """
    if not (request.user.is_superuser or request.user.is_staff):
        return redirect('orders:user_orders')

    status_filter = request.GET.get('status')
    orders = Order.objects.all().order_by('-created_at')

    if status_filter:
        orders = orders.filter(status=status_filter)

    return render(request, 'orders/admin_order_list.html', {
        'orders': orders,
        'STATUS_CHOICES': [choice for choice in Order.STATUS_CHOICES]
    })


@login_required
def user_orders_view(request):
    """
    Список заказов текущего пользователя (мои заказы)
    """
    status_filter = request.GET.get('status')
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    if status_filter:
        orders = orders.filter(status=status_filter)

    return render(request, 'orders/user_order_list.html', {
        'orders': orders,
        'STATUS_CHOICES': [choice for choice in Order.STATUS_CHOICES]
    })


@login_required
def order_detail_view(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        raise Http404("Заказ не найден")

    # Проверяем права на просмотр заказа
    is_owner = request.user == order.user
    is_admin = request.user.is_superuser
    is_manager = request.user.is_staff

    if not (is_admin or is_manager or is_owner):
        raise PermissionDenied("У вас нет прав на просмотр этого заказа")

    is_point_manager = False
    if hasattr(order, 'pickup_point') and order.pickup_point:
        is_point_manager = request.user.points.filter(id=order.pickup_point.id).exists()

    return render(request, 'orders/order_detail.html', {
        'order': order,
        'order_items': order.items.all(),
        'is_point_manager': is_point_manager,
        'STATUS_CHOICES': [choice for choice in Order.STATUS_CHOICES]
    })


@login_required
def order_confirm_view(request):
    """
    Оформление заказа
    """
    # Получаем товары из корзины текущего пользователя
    cart_items = CartItem.objects.filter(cart__user=request.user).select_related('product')

    if not cart_items.exists():
        messages.warning(request, "Корзина пуста")
        return redirect('cart:cart_view')

    total_price = sum(item.product.price * item.quantity for item in cart_items)
    points = Point.objects.all()

    if request.method == 'POST':
        form = OrderConfirmForm(request.POST)
        if form.is_valid():
            delivery_type = form.cleaned_data.get('delivery_type')
            pickup_point_id = form.cleaned_data.get('pickup_point')
            address = form.cleaned_data.get('address', '')
            delivery_date_str = form.cleaned_data.get('delivery_date')
            time_slot = form.cleaned_data.get('time_slot')
            name = form.cleaned_data.get('name')
            phone = form.cleaned_data.get('phone')
            email = form.cleaned_data.get('email')
            payment_type = form.cleaned_data.get('payment_type')

            try:
                with transaction.atomic():
                    from datetime import date, datetime

                    # Парсим дату и время доставки
                    delivery_date = None
                    if delivery_date_str:
                        try:
                            delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d').date()
                        except ValueError:
                            raise forms.ValidationError("Неверный формат даты")

                    # Проверка обязательных данных для доставки
                    if delivery_type == 'courier' and (not delivery_date or not time_slot):
                        raise forms.ValidationError("Выбрав доставку, необходимо указать дату и тайм-слот.")

                    # Создаём заказ
                    order = Order.objects.create(
                        user=request.user,
                        name=name,
                        phone=phone,
                        email=email,
                        delivery_type=delivery_type,
                        address=address,
                        delivery_date=delivery_date,
                        time_slot=time_slot,
                        status='created',
                        total_price=total_price,
                        payment_status='pending',
                        payment_type=payment_type
                    )

                    # Устанавливаем пункт самовывоза
                    if delivery_type == 'pickup' and pickup_point_id:
                        try:
                            pickup_point = Point.objects.get(id=pickup_point_id)
                            order.pickup_point = pickup_point
                            order.save()
                        except Point.DoesNotExist:
                            messages.error(request, "Пункт самовывоза не найден")
                            return redirect('orders:checkout')

                    # Переносим товары в заказ
                    for cart_item in cart_items:
                        product = cart_item.product
                        quantity_needed = cart_item.quantity

                        if delivery_type == 'courier':
                            warehouse = Point.objects.filter(is_warehouse=True).first()
                            if not warehouse:
                                raise Exception("Нет доступного склада")

                            remaining_quantity = quantity_needed
                            all_points = Point.objects.all()

                            for point in all_points:
                                try:
                                    pinv = PointInventory.objects.select_for_update().get(product=product, point=point)
                                except PointInventory.DoesNotExist:
                                    continue

                                if pinv.quantity >= remaining_quantity:
                                    pinv.quantity -= remaining_quantity
                                    pinv.save()
                                    StockHistory.objects.create(
                                        product=product,
                                        point=point,
                                        quantity=remaining_quantity,
                                        action='writeoff',
                                        comment=f"Списано с '{point.name}' при оформлении заказа #{order.id}"
                                    )
                                    remaining_quantity = 0
                                    break
                                else:
                                    take_amount = pinv.quantity
                                    pinv.quantity = 0
                                    pinv.save()
                                    StockHistory.objects.create(
                                        product=product,
                                        point=point,
                                        quantity=take_amount,
                                        action='writeoff',
                                        comment=f"Частичное списание с '{point.name}' при оформлении заказа #{order.id}"
                                    )
                                    remaining_quantity -= take_amount

                            if remaining_quantity > 0:
                                raise Exception(f"Недостаточно '{product.name}' для выполнения заказа")

                        elif delivery_type == 'pickup' and pickup_point_id:
                            try:
                                pickup_point = Point.objects.get(id=pickup_point_id)
                                order.pickup_point = pickup_point
                                order.save()
                            except Point.DoesNotExist:
                                raise Exception("Пункт самовывоза не найден")

                            warehouse = Point.objects.filter(is_warehouse=True).first()
                            if not warehouse:
                                raise Exception("Нет доступного склада")

                            remaining_quantity = quantity_needed
                            try:
                                pinv_warehouse = PointInventory.objects.select_for_update().get(
                                    product=product,
                                    point=warehouse
                                )
                                if pinv_warehouse.quantity >= remaining_quantity:
                                    pinv_warehouse.quantity -= remaining_quantity
                                    pinv_warehouse.save()
                                    StockHistory.objects.create(
                                        product=product,
                                        point=warehouse,
                                        quantity=remaining_quantity,
                                        action='writeoff',
                                        comment=f"Списано с '{warehouse.name}' при оформлении заказа #{order.id}"
                                    )
                                    remaining_quantity = 0
                                else:
                                    take_amount = pinv_warehouse.quantity
                                    pinv_warehouse.quantity = 0
                                    pinv_warehouse.save()
                                    StockHistory.objects.create(
                                        product=product,
                                        point=warehouse,
                                        quantity=take_amount,
                                        action='writeoff',
                                        comment=f"Частичное списание с '{warehouse.name}' при оформлении заказа #{order.id}"
                                    )
                                    remaining_quantity -= take_amount
                            except PointInventory.DoesNotExist:
                                pass

                            other_points = PointInventory.objects.select_for_update().filter(
                                product=product,
                                quantity__gt=0
                            ).exclude(point_id=warehouse.id).order_by('-quantity')

                            for inv in other_points:
                                if remaining_quantity <= 0:
                                    break

                                take_amount = min(inv.quantity, remaining_quantity)
                                inv.quantity -= take_amount
                                inv.save()
                                remaining_quantity -= take_amount

                                StockHistory.objects.create(
                                    product=product,
                                    point=inv.point,
                                    quantity=take_amount,
                                    action='writeoff',
                                    comment=f"Списано с '{inv.point.name}' при оформлении заказа #{order.id}"
                                )

                            if remaining_quantity > 0:
                                raise Exception(f"Недостаточно '{product.name}' для выполнения заказа")

                            # Перемещаем товар на точку самовывоза
                            try:
                                pinv_pickup = PointInventory.objects.select_for_update().get(
                                    product=product,
                                    point=pickup_point
                                )
                            except PointInventory.DoesNotExist:
                                pinv_pickup = PointInventory.objects.create(
                                    product=product,
                                    point=pickup_point,
                                    quantity=0
                                )

                            pinv_pickup.quantity += quantity_needed
                            pinv_pickup.save()

                            StockHistory.objects.create(
                                product=product,
                                point=pickup_point,
                                quantity=quantity_needed,
                                action='add',
                                comment=f"Добавлено на '{pickup_point.name}' при оформлении заказа #{order.id}"
                            )

                        # Добавляем товар в заказ
                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity_needed,
                            price=product.price
                        )

                    # Очищаем корзину после успешного оформления
                    cart_items.delete()

                    # Отправляем email только при онлайн-оплате
                    if payment_type == 'online':
                        payment_url = request.build_absolute_uri(reverse('orders:payment_process', args=[order.id]))
                        html_message = render_to_string('orders/payment_confirmation_email.html', {
                            'order': order,
                            'payment_url': payment_url
                        })
                        plain_message = strip_tags(html_message)

                        send_mail(
                            subject=f"Подтверждение заказа #{order.id}",
                            message=plain_message,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[request.user.email],
                            html_message=html_message,
                            fail_silently=False
                        )
                        messages.success(request, "Письмо с информацией по оплате отправлено на ваш email.")
                    elif payment_type == 'cash':
                        messages.success(request, "Заказ оформлен успешно!")

                    return redirect('orders:order_detail', order_id=order.id)

            except Exception as e:
                messages.error(request, f"Ошибка при оформлении заказа: {str(e)}")
                return redirect('orders:checkout')
        else:
            messages.error(request, "Форма заполнена неверно.")
            print(form.errors)
            return redirect('orders:checkout')
    else:
        form = OrderConfirmForm()

    return render(request, 'orders/checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'total_price': total_price,
        'points': points
    })


@login_required
def update_order_status(request, order_id):
    """
    Обновление статуса заказа
    """
    order = get_object_or_404(Order, id=order_id)

    # Статусы, которые нельзя менять
    forbidden_statuses = ['cancelled', 'delivered']

    if order.status in forbidden_statuses:
        messages.warning(
            request,
            f"Заказ с статусом '{order.get_status_display()}' редактировать нельзя."
        )
        return redirect('orders:order_detail', order_id=order.id)

    # Проверяем права
    if not request.user.is_superuser and request.user != order.manager:
        messages.error(request, "У вас нет прав на изменение этого заказа")
        return redirect('orders:order_detail', order_id=order.id)

    if request.method == 'POST':
        new_status = request.POST.get('status')

        valid_statuses = [key for key, _ in Order.STATUS_CHOICES]
        if new_status in valid_statuses:
            old_status = order.status
            order.status = new_status
            order.save()

            # Отправляем уведомление
            send_order_status_email(order, order.user)

            # Возвращаем товар при отмене
            if new_status == 'cancelled':
                try:
                    with transaction.atomic():
                        for item in order.items.all():
                            product = item.product
                            quantity = item.quantity

                            if order.delivery_type == 'pickup' and order.pickup_point:
                                point = order.pickup_point
                                pinv = PointInventory.objects.select_for_update().get(product=product, point=point)
                                pinv.quantity += quantity
                                pinv.save()
                            elif order.delivery_type == 'courier':
                                warehouse = Point.objects.filter(is_warehouse=True).first()
                                if not warehouse:
                                    raise Exception("Нет доступного склада")

                                pinv = PointInventory.objects.select_for_update().get(product=product, point=warehouse)
                                pinv.quantity += quantity
                                pinv.save()

                except Exception as e:
                    messages.error(request, f"Ошибка возврата товара: {str(e)}")
                    order.status = old_status  # Откатываем статус
                    order.save()
                    return redirect('orders:order_detail', order_id=order.id)

            messages.success(request, f"Статус заказа изменён на {order.get_status_display()}")
        else:
            messages.error(request, "Неверный статус")

    return redirect('orders:order_detail', order_id=order_id)


@login_required
def profile_orders_view(request):
    """
    Отображение заказов в профиле
    """
    return redirect('orders:user_orders')


@login_required
def payment_confirmation(request, order_id):
    """
    Подтверждение оплаты (эмуляция)
    """
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        messages.warning(request, "Заказ не найден.")
        return redirect('orders:user_orders')

    if order.payment_type == 'cash':
        messages.success(request, "Заказ уже принят. Оплата производится при получении.")
        return redirect('orders:order_detail', order_id=order.id)

    if request.method == 'POST':
        card_number = request.POST.get('card_number')

        if card_number and len(card_number) >= 16:
            # Эмуляция успешной оплаты
            order.status = 'accepted'
            order.payment_status = 'paid'
            order.save()

            from .utils import send_order_status_email
            send_order_status_email(order, order.user)

            messages.success(request, "Оплата прошла успешно! Ваш заказ принят к выполнению.")
        else:
            messages.error(request, "Неверный формат номера карты.")

    return render(request, 'orders/payment_confirmation.html', {
        'order': order
    })


@login_required
def payment_process(request, order_id):
    """
    Эмуляция процесса оплаты
    """
    try:
        order = get_object_or_404(Order, id=order_id, user=request.user)
    except Exception as e:
        messages.warning(request, "Заказ не найден.")
        return redirect('orders:user_orders')

    if request.method == 'POST':
        card_number = request.POST.get('card_number')
        if card_number and len(card_number) >= 16:
            # Эмуляция успешной оплаты
            order.status = 'accepted'
            order.payment_status = 'paid'
            order.save()
            messages.success(request, "Оплата прошла успешно! Ваш заказ принят к выполнению.")
        else:
            messages.error(request, "Неверный формат номера карты.")

    elif request.method == 'GET':
        # Эмуляция оплаты через QR-код
        order.status = 'accepted'
        order.payment_status = 'paid'
        order.save()
        messages.success(request, "Оплата прошла успешно! Ваш заказ принят к выполнению.")

    return redirect('orders:order_detail', order_id=order.id)
