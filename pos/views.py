# pos/views.py
from django.contrib.auth.decorators import user_passes_test, login_required
from django.core.checks import messages
from django.shortcuts import render, get_object_or_404, redirect

from inventory.models import PointInventory
from users.decorators import permission_required
from .models import Point
from .forms import PointForm
from orders.models import Order
from django.db import models


def is_manager(user):
    """
    Проверяет, является ли пользователь менеджером.
    Пользователь считается менеджером, если он суперпользователь или состоит в группе 'Менеджеры точек'.

    Args:
        user: Объект пользователя Django.

    Returns:
        bool: True, если пользователь является менеджером.
    """
    return user.is_superuser or user.groups.filter(name='Менеджеры точек').exists()


@permission_required
def point_list_view(request):
    """
    Отображает список всех пунктов выдачи.
    Для каждого пункта подсчитывает общее количество и сумму заказов.
    """

    points = Point.objects.all()

    # Добавляем информацию о заказах к каждой точке
    for point in points:
        point.total_orders = Order.objects.filter(pickup_point=point).count()
        point.total_amount = Order.objects.filter(pickup_point=point).aggregate(total=models.Sum('total_price'))['total'] or 0

    return render(request, 'pos/point_list.html', {'points': points})


@user_passes_test(is_manager)
def point_detail_view(request, point_id):
    """
    Отображает детали конкретного пункта выдачи.
    Включает текущие остатки товаров на этом пункте.

    Args:
        point_id (int): ID пункта выдачи.

    Returns:
        HttpResponse: Отрендеренная страница с информацией о пункте.
    """

    point = get_object_or_404(Point, id=point_id)
    inventories = PointInventory.objects.filter(point=point).select_related('product')
    return render(request, 'pos/point_detail.html', {
        'point': point,
        'inventories': inventories
    })


def point_create_view(request):
    """
    Представление для создания нового пункта выдачи.
    Использует форму PointForm.
    """

    if request.method == 'POST':
        form = PointForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pos:point_list')
    else:
        form = PointForm()

    return render(request, 'pos/point_form.html', {'form': form})


def point_update_view(request, point_id):
    """
    Представление для редактирования существующего пункта выдачи.
    Использует форму PointForm.

    Args:
        point_id (int): ID пункта выдачи.

    Returns:
        HttpResponse: Отрендеренная форма для редактирования.
    """

    point = get_object_or_404(Point, id=point_id)
    if request.method == 'POST':
        form = PointForm(request.POST, instance=point)
        if form.is_valid():
            form.save()
            return redirect('pos:point_list')
    else:
        form = PointForm(instance=point)

    return render(request, 'pos/point_form.html', {'form': form, 'point': point})


def point_delete_view(request, point_id):
    """
    Представление для удаления пункта выдачи.

    Args:
        point_id (int): ID пункта выдачи.

    Returns:
        HttpResponse: Перенаправление на список пунктов после удаления.
    """

    point = get_object_or_404(Point, id=point_id)
    if request.method == 'POST':
        point.delete()
        return redirect('pos:point_list')

    return render(request, 'pos/point_confirm_delete.html', {'point': point})


@login_required
def edit_point_view(request, point_id):
    """
    Редактирование пункта выдачи.
    Позволяет менеджерам обновлять данные о пункте выдачи.
    """

    point = get_object_or_404(Point, id=point_id)

    if request.method == 'POST':
        form = PointForm(request.POST, instance=point)
        if form.is_valid():
            form.save()
            messages.success(request, "Пункт выдачи успешно обновлён")
            return redirect('pos:point_list')
        else:
            messages.error(request, "Ошибка при обновлении пункта выдачи")
    else:
        form = PointForm(instance=point)

    return render(request, 'pos/edit_point.html', {
        'form': form,
        'point': point
    })
