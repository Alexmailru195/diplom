# orders/views.py

from datetime import datetime, date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import Http404
from django.shortcuts import render, redirect

from cart.models import CartItem
from inventory.models import PointInventory
from pos.models import Point
from shop_project import settings
from .forms import OrderConfirmForm
from .models import Order, OrderItem
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


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
        'order_items': order.items.all()
    })


@login_required(login_url='users:login')
def order_confirm_view(request):
    """
    Оформление заказа
    """
    cart_items = CartItem.objects.filter(cart__user=request.user).select_related('product')
    if not cart_items.exists():
        messages.warning(request, "Корзина пуста")
        return redirect('products:product_list')

    total_price = sum(item.product.price * item.quantity for item in cart_items)
    points = Point.objects.all()

    today = date.today()
    tomorrow = today + timedelta(days=1)
    next_month = today + timedelta(days=30)

    if request.method == 'POST':
        form = OrderConfirmForm(request.POST)

        if form.is_valid():
            delivery_type = form.cleaned_data.get('delivery_type')
            pickup_point_id = form.cleaned_data.get('pickup_point')
            address = form.cleaned_data.get('address', '')
            delivery_date_str = form.cleaned_data.get('delivery_date')
            time_slot = form.cleaned_data.get('time_slot')

            try:
                with transaction.atomic():
                    # Парсим дату безопасным способом
                    if delivery_date_str and isinstance(delivery_date_str, str):
                        try:
                            delivery_date = datetime.strptime(delivery_date_str, "%d.%m.%Y").date()
                        except ValueError:
                            raise ValidationError("Неверная дата доставки")
                    else:
                        delivery_date = None

                    if delivery_date_str and not delivery_date:
                        raise ValidationError("Неверная дата доставки")

                    # Создаем заказ
                    order = Order.objects.create(
                        user=request.user,
                        name=form.cleaned_data['name'],
                        phone=form.cleaned_data['phone'],
                        email=form.cleaned_data.get('email'),
                        delivery_type=delivery_type,
                        address=address,
                        delivery_date=delivery_date,
                        time_slot=time_slot,
                        payment_type=form.cleaned_data['payment_type'],
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

                    # Отправляем email
                    if request.user.email:
                        subject = 'Новый заказ'
                        html_message = render_to_string('orders/order_confirmation_email.html', {
                            'order': order,
                            'user': request.user
                        })
                        plain_message = strip_tags(html_message)
                        from_email = settings.DEFAULT_FROM_EMAIL
                        to_email = [request.user.email]

                        try:
                            send_mail(subject, plain_message, from_email, to_email, html_message=html_message,
                                      fail_silently=False)
                        except Exception as e:
                            print(f"Ошибка отправки email: {e}")
                            messages.warning(request, "Заказ оформлен, но не удалось отправить email")

                    return redirect('orders:order_detail', order_id=order.id)

            except Point.DoesNotExist:
                messages.error(request, "Пункт самовывоза не найден")
                return redirect('orders:checkout')
            except PointInventory.DoesNotExist:
                messages.error(request, "Инвентарь не найден")
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
            'points': points,
            'tomorrow': tomorrow.strftime('%Y-%m-%d'),
            'next_month': next_month.strftime('%Y-%m-%d')
        })
