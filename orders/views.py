# orders/views.py

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib import messages
from django.utils.dateparse import parse_date, parse_time
from cart.models import CartItem
from .models import Order, OrderItem
from pos.models import Point
from inventory.models import PointInventory
from .forms import OrderConfirmForm


@login_required
def order_list_view(request):
    """
    Список заказов пользователя
    """
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail_view(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        raise Http404("Заказ не найден или доступ запрещён")
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'order_items': order.items.all()
    })


@login_required
def checkout_view(request):
    cart_items = CartItem.objects.filter(cart__user=request.user).select_related('product')
    if not cart_items:
        messages.warning(request, "Корзина пуста")
        return redirect('products:product_list')

    total_price = sum(item.product.price * item.quantity for item in cart_items)
    points = Point.objects.all()

    if request.method == 'POST':
        form = OrderConfirmForm(request.POST)
        if form.is_valid():
            delivery_type = form.cleaned_data.get('delivery_type')
            pickup_point_id = form.cleaned_data.get('pickup_point')  # ← это id, а не объект
            address = form.cleaned_data.get('address', '')
            delivery_date_str = form.cleaned_data.get('delivery_date')
            delivery_time_str = form.cleaned_data.get('delivery_time')

            try:
                with transaction.atomic():
                    delivery_date = parse_date(delivery_date_str) if delivery_date_str else None
                    delivery_time = parse_time(delivery_time_str) if delivery_time_str else None

                    if delivery_date_str and not delivery_date:
                        messages.error(request, "Неверная дата доставки")
                        return redirect('orders:checkout')
                    if delivery_time_str and not delivery_time:
                        messages.error(request, "Неверное время доставки")
                        return redirect('orders:checkout')

                    # Создаем заказ
                    order = Order.objects.create(
                        user=request.user,
                        name=form.cleaned_data['name'],
                        phone=form.cleaned_data['phone'],
                        email=form.cleaned_data.get('email'),
                        delivery_type=delivery_type,
                        address=address,
                        delivery_date=delivery_date,
                        delivery_time=delivery_time,
                        status='created',
                        total_price=total_price
                    )

                    # Устанавливаем пункт самовывоза
                    if delivery_type == 'pickup' and pickup_point_id:
                        try:
                            pickup_point = Point.objects.get(id=pickup_point_id)
                            order.pickup_point = pickup_point
                            order.save()
                        except Point.DoesNotExist:
                            messages.error(request, "Точка выдачи не найдена")
                            return redirect('orders:checkout')

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
                    for cart_item in cart_items:
                        product = cart_item.product
                        quantity = cart_item.quantity

                        if delivery_type == 'pickup' and pickup_point_id:
                            pinv = PointInventory.objects.select_for_update().get(
                                product=product,
                                point_id=pickup_point_id
                            )
                            if pinv.quantity < quantity:
                                messages.error(request, f"Недостаточно '{product.name}' на пункте выдачи")
                                return redirect('orders:checkout')
                            pinv.quantity -= quantity
                            pinv.save()

                        elif delivery_type == 'courier':
                            warehouse = Point.objects.filter(is_warehouse=True).first()
                            if not warehouse:
                                messages.error(request, "Нет доступных складов для доставки")
                                return redirect('orders:checkout')

                            pinv = PointInventory.objects.select_for_update().get(
                                product=product,
                                point_id=warehouse.id
                            )
                            if pinv.quantity < quantity:
                                best_inv = PointInventory.objects.select_for_update().filter(
                                    product=product,
                                    quantity__gte=quantity
                                ).order_by('-quantity').first()

                                if best_inv:
                                    best_inv.quantity -= quantity
                                    best_inv.save()
                                else:
                                    messages.error(request, f"Нет достаточного количества '{product.name}' для доставки")
                                    return redirect('orders:checkout')

                            pinv.quantity -= quantity
                            pinv.save()

                    # Очищаем корзину
                    cart_items.delete()
                    messages.success(request, "Заказ оформлен успешно!")
                    return redirect('orders:order_detail', order_id=order.id)

            except Exception as e:
                messages.error(request, f"Системная ошибка: {str(e)}")
                return redirect('orders:checkout')

        else:
            messages.error(request, "Форма заполнена неверно")
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


@login_required(login_url='users:login')
def order_confirm_view(request):
    cart_items = CartItem.objects.filter(cart__user=request.user).select_related('product')
    if not cart_items:
        messages.warning(request, "Корзина пуста")
        return redirect('products:product_list')

    total_price = sum(item.product.price * item.quantity for item in cart_items)
    points = Point.objects.all()

    if request.method == 'POST':
        form = OrderConfirmForm(request.POST)
        if form.is_valid():
            delivery_type = form.cleaned_data.get('delivery_type')
            pickup_point_id = form.cleaned_data.get('pickup_point')
            address = form.cleaned_data.get('address', '')
            delivery_date_str = form.cleaned_data.get('delivery_date')
            delivery_time_str = form.cleaned_data.get('delivery_time')

            try:
                with transaction.atomic():
                    delivery_date = parse_date(delivery_date_str) if delivery_date_str else None
                    delivery_time = parse_time(delivery_time_str) if delivery_time_str else None

                    if delivery_date_str and not delivery_date:
                        raise ValidationError("Неверная дата доставки")
                    if delivery_time_str and not delivery_time:
                        raise ValidationError("Неверное время доставки")

                    # Создаем заказ
                    order = Order.objects.create(
                        user=request.user,
                        name=form.cleaned_data['name'],
                        phone=form.cleaned_data['phone'],
                        email=form.cleaned_data.get('email'),
                        delivery_type=delivery_type,
                        address=address,
                        delivery_date=delivery_date,
                        delivery_time=delivery_time,
                        status='created',
                        total_price=total_price
                    )

                    # Устанавливаем пункт самовывоза
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
                    for cart_item in cart_items:
                        product = cart_item.product
                        quantity = cart_item.quantity

                        if delivery_type == 'pickup' and pickup_point_id:
                            pinv = PointInventory.objects.select_for_update().get(
                                product=product,
                                point_id=pickup_point_id
                            )
                            if pinv.quantity < quantity:
                                raise ValidationError(f"Недостаточно '{product.name}' на пункте выдачи")

                            pinv.quantity -= quantity
                            pinv.save()
                        elif delivery_type == 'courier':
                            warehouse = Point.objects.filter(is_warehouse=True).first()
                            if not warehouse:
                                raise ValidationError("Нет доступных складов для доставки")

                            pinv = PointInventory.objects.select_for_update().get(
                                product=product,
                                point_id=warehouse.id
                            )
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

            except Point.DoesNotExist:
                messages.error(request, "Пункт самовывоза не найден")
                return redirect('orders:checkout')
            except ValidationError as e:
                messages.error(request, str(e))
                return redirect('orders:checkout')
            except Exception as e:
                messages.error(request, f"Системная ошибка: {str(e)}")
                return redirect('orders:checkout')

        else:
            messages.error(request, "Форма заполнена неверно")
            print(form.errors)
            return redirect('orders:checkout')

    else:
        form = OrderConfirmForm()
        return render(request, 'orders/order_confirm.html', {
            'form': form,
            'cart_items': cart_items,
            'total_price': total_price,
            'points': points
        })
