# inventory/views.py

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect, get_object_or_404

from pos.models import Point
from products.models import Product
from users.decorators import permission_required
from .forms import InventoryMoveForm
from .forms import PointInventoryForm
from django.db import transaction
from .models import PointInventory, StockMovement, StockHistory


def is_manager(user):
    """
    Проверяет, является ли пользователь менеджером (админ, стафф или модератор).
    Используется в декораторе @user_passes_test.

    Args:
        user: Объект пользователя Django.

    Returns:
        bool: True, если пользователь является менеджером.
    """
    return user.is_superuser or user.is_staff or user.groups.filter(name='Модераторы').exists()


@user_passes_test(is_manager)
def move_inventory(request):
    """
    Представление для перемещения товара между точками выдачи.
    Работает только для авторизованных менеджеров и админов.
    """

    form = InventoryMoveForm()

    if request.method == 'POST':
        form = InventoryMoveForm(request.POST)

        if form.is_valid():
            product = form.cleaned_data['product']
            from_point = form.cleaned_data['from_point']
            to_point = form.cleaned_data['to_point']
            quantity = form.cleaned_data['quantity']

            try:
                with transaction.atomic():
                    from_inv, created = PointInventory.objects.select_for_update().get_or_create(
                        product=product,
                        point=from_point,
                        defaults={'quantity': 0}
                    )

                    if from_inv.quantity < quantity:
                        messages.error(request, "Недостаточно товара на исходной точке")
                        return render(request, 'inventory/move_form.html', {'form': form})

                    to_inv, created = PointInventory.objects.select_for_update().get_or_create(
                        product=product,
                        point=to_point,
                        defaults={'quantity': 0}
                    )

                    from_inv.quantity -= quantity
                    from_inv.save()

                    to_inv.quantity += quantity
                    to_inv.save()

                    # Создаем запись в StockMovement (если нужно)
                    StockMovement.objects.create(
                        movement_type='move',
                        product_inventory=from_inv,
                        from_point=from_point,
                        to_point=to_point,
                        quantity=quantity
                    )

                    messages.success(request, "Товар успешно перемещён")
                    return redirect('inventory:stock_history')

            except Exception as e:
                messages.error(request, f"Ошибка при перемещении: {e}")
                return redirect('inventory:move_inventory')
        else:
            messages.error(request, "Форма заполнена неверно")
            print(form.errors)

    return render(request, 'inventory/move_form.html', {'form': form})


@permission_required
def inventory_list_view(request):
    """
    Список остатков товаров на всех точках выдачи.
    Включает фильтрацию по товару и точке.
    """

    # Получаем все товары и точки для фильтрации
    products = Product.objects.all()
    points = Point.objects.all()

    # Получаем параметры фильтрации
    product_id = request.GET.get('product')
    point_id = request.GET.get('point')

    # Фильтруем остатки
    inventories = PointInventory.objects.all().order_by('-updated_at')

    if product_id:
        inventories = inventories.filter(product_id=product_id)

    if point_id:
        inventories = inventories.filter(point_id=point_id)

    return render(request, 'inventory/inventory_list.html', {
        'inventories': inventories,
        'products': products,
        'points': points
    })


def inventory_detail_view(request, inventory_id):
    """
    Отображает детали конкретного инвентаря и историю его изменений.

    Args:
        inventory_id (int): ID записи PointInventory.

    Returns:
        HttpResponse: Отрендеренная страница с информацией об инвентаре.
    """

    inventory = PointInventory.objects.get(id=inventory_id)
    movements = StockMovement.objects.filter(product_inventory=inventory).order_by('-timestamp')
    return render(request, 'inventory/inventory_detail.html', {
        'inventory': inventory,
        'movements': movements
    })


@permission_required
def add_inventory(request):
    """
    Представление для добавления или обновления количества товара на точке выдачи.
    """

    if request.method == 'POST':
        form = PointInventoryForm(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            point = form.cleaned_data['point']
            quantity = form.cleaned_data['quantity']

            with transaction.atomic():
                pinv, created = PointInventory.objects.select_for_update().get_or_create(
                    product=product,
                    point=point,
                    defaults={'quantity': 0}
                )

                if not created:
                    pinv.quantity += quantity
                else:
                    pinv.quantity = quantity

                pinv.save()  # Логика записи истории уже внутри метода save()

            messages.success(request, f"{'Создана' if created else 'Обновлена'} запись для '{product.name}' на '{point.name}'. Новое количество: {pinv.quantity}")
            return redirect('inventory:stock_list')
        else:
            messages.error(request, "Форма заполнена неверно.")
            print(form.errors)

    else:
        form = PointInventoryForm()

    return render(request, 'inventory/add_inventory.html', {'form': form})


def stock_movement_history(request):
    """
    История операций перемещения товаров между точками.

    Returns:
        HttpResponse: Отрендеренная страница с историей.
    """

    movements = StockMovement.objects.select_related('from_point', 'to_point').all().order_by('-timestamp')
    return render(request, 'inventory/stock_history.html', {'movements': movements})


def low_stock_alert(request):
    """
    Отображает список товаров с низким уровнем запасов.

    Returns:
        HttpResponse: Отрендеренная страница с уведомлениями о низком уровне запасов.
    """

    threshold = 5
    inventories = PointInventory.objects.filter(quantity__lt=threshold)
    return render(request, 'inventory/low_stock.html', {'inventories': inventories})


@login_required
def stock_history(request):
    """
    История операций со складом: списания, добавления и перемещения.

    Returns:
        HttpResponse: Отрендеренная страница с историей.
    """

    history = StockHistory.objects.all().order_by('-created_at')

    action_filter = request.GET.get('action')

    # Получаем все возможные действия из модели
    ACTION_CHOICES = dict(StockHistory.ACTION_CHOICES)

    # Фильтруем историю
    if action_filter and action_filter in ACTION_CHOICES:
        history = StockHistory.objects.filter(action=action_filter).order_by('-created_at')
    else:
        history = StockHistory.objects.all().order_by('-created_at')

    return render(request, 'inventory/stock_history.html', {
        'history': history,
        'ACTION_CHOICES': ACTION_CHOICES
    })


@login_required
def writeoff_inventory(request, inventory_id):
    """
    Списание товара с точки выдачи.
    """

    try:
        inv = get_object_or_404(PointInventory, id=inventory_id)

        if request.method == 'POST':
            quantity = int(request.POST.get('quantity'))
            comment = request.POST.get('comment')

            if quantity <= 0 or quantity > inv.quantity:
                messages.error(request, "Неверное количество для списания")
                return redirect('inventory:inventory_list')

            # Обновляем остаток
            inv.quantity -= quantity
            inv.save()

            # Сохраняем историю
            StockHistory.objects.create(
                product=inv.product,
                point_from=inv.point,
                quantity=quantity,
                action='writeoff',
                comment=comment
            )

            messages.success(request, f"Списано {quantity} единиц товара '{inv.product.name}' с точки '{inv.point.name}'.")
            return redirect('inventory:inventory_list')
    except Exception as e:
        messages.error(request, f"Ошибка при списании товара: {e}")
        return redirect('inventory:inventory_list')
