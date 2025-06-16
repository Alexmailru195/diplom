# orders/views.py

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.http import Http404

import pos
from .models import Order, OrderItem
from cart.models import CartItem
from pos.models import Point
from inventory.models import PointInventory
from .forms import OrderConfirmForm


@login_required
def order_list_view(request):
    """
    Список всех заказов (для админов)
    """
    if not request.user.is_superuser:
        return redirect('orders:all_orders')

    status_filter = request.GET.get('status')
    orders = Order.objects.all().order_by('-created_at')

    if status_filter:
        orders = orders.filter(status=status_filter)

    return render(request, 'orders/admin_order_list.html', {
        'orders': orders,
        'STATUS_CHOICES': [choice for choice in Order.STATUS_CHOICES],
    })


@login_required
def all_orders_view(request):
    """
    Список всех заказов (для админов)
    """
    return order_list_view(request)


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
        'STATUS_CHOICES': [choice for choice in Order.STATUS_CHOICES],
    })


@login_required
def order_detail_view(request, order_id):
    try:
        # Показываем заказ, если он принадлежит пользователю,
        # или это админ, или менеджер точки
        if request.user.is_superuser:
            order = Order.objects.get(id=order_id)
        elif request.user == pos.manager:
            order = Order.objects.get(id=order_id)
        else:
            order = Order.objects.get(id=order_id, user=request.user)

    except Order.DoesNotExist:
        raise Http404("Заказ не найден или у вас нет прав на его просмотр")

    return render(request, 'orders/order_detail.html', {
        'order': order,
        'order_items': order.items.all(),
    })


@login_required
def order_confirm_view(request):
    """
    Оформление заказа
    """
    cart_items = CartItem.objects.filter(cart__user=request.user).select_related('product')

    if not cart_items:
        messages.warning(request, "Ваша корзина пуста.")
        return redirect('products:product_list')

    total_price = sum(item.product.price * item.quantity for item in cart_items)

    if request.method == 'POST':
        form = OrderConfirmForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            phone = form.cleaned_data['phone']
            email = form.cleaned_data.get('email')
            delivery_type = form.cleaned_data['delivery_type']
            address = form.cleaned_data.get('address') if delivery_type == 'courier' else ''
            delivery_date_str = form.cleaned_data.get('delivery_date')
            pickup_point_id = form.cleaned_data.get('pickup_point')

            try:
                with transaction.atomic():
                    from datetime import date, time
                    delivery_date = date.fromisoformat(delivery_date_str) if delivery_date_str else None

                    # Создаем заказ
                    order = Order.objects.create(
                        user=request.user,
                        name=name,
                        phone=phone,
                        email=email,
                        delivery_type=delivery_type,
                        address=address,
                        delivery_date=delivery_date,
                        status='created',
                        total_price=total_price
                    )

                    # Устанавливаем точку самовывоза
                    if delivery_type == 'pickup' and pickup_point_id:
                        point = Point.objects.get(id=pickup_point_id)
                        order.pickup_point = point
                        order.save()

                    # Переносим товары в заказ
                    for cart_item in cart_items:
                        product = cart_item.product
                        quantity = cart_item.quantity

                        OrderItem.objects.create(
                            order=order,
                            product=product,
                            quantity=quantity,
                            price=product.price
                        )

                        # Списание остатков
                        if delivery_type == 'pickup' and pickup_point_id:
                            pinv = PointInventory.objects.select_for_update().get(product=product, point_id=pickup_point_id)
                            if pinv.quantity < quantity:
                                raise ValidationError(f"Недостаточно '{product.name}' на пункте самовывоза")
                            pinv.quantity -= quantity
                            pinv.save()
                        elif delivery_type == 'courier':
                            warehouse = Point.objects.filter(is_warehouse=True).first()
                            if not warehouse:
                                raise ValidationError("Нет доступных складов для доставки")

                            pinv = PointInventory.objects.select_for_update().get(product=product, point=warehouse)
                            if pinv.quantity < quantity:
                                best_inv = PointInventory.objects.select_for_update().filter(
                                    product=product,
                                    quantity__gte=quantity
                                ).order_by('-quantity').first()
                                if best_inv:
                                    best_inv.quantity -= quantity
                                    best_inv.save()
                                else:
                                    raise ValidationError(f"Нет достаточного количества '{product.name}' для доставки")
                            pinv.quantity -= quantity
                            pinv.save()

                    # Очищаем корзину
                    cart_items.delete()

                    messages.success(request, "Заказ оформлен успешно!")
                    return redirect('orders:order_detail', order_id=order.id)

            except Exception as e:
                messages.error(request, f"Ошибка при оформлении заказа: {str(e)}")
                return redirect('orders:checkout')

    else:
        form = OrderConfirmForm()

    points = Point.objects.all()
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
