# inventory/views.py

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect

from users.decorators import permission_required
from .forms import InventoryMoveForm
from .forms import PointInventoryForm
from django.db import transaction
from .models import PointInventory, StockMovement


def is_manager(user):
    return user.is_superuser or user.is_staff or user.groups.filter(name='Модераторы').exists()


# inventory/views.py
@user_passes_test(is_manager)
def move_inventory(request):
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
                    # Получаем инвентарь из точки отправления
                    from_inv, created = PointInventory.objects.get_or_create(
                        product=product,
                        point=from_point,
                        defaults={'quantity': 0}
                    )

                    if from_inv.quantity < quantity:
                        messages.error(request, "Недостаточно товара на исходной точке")
                        return render(request, 'inventory/move_form.html', {'form': form})

                    # Получаем или создаём инвентарь целевой точки
                    to_inv, created = PointInventory.objects.select_for_update().get_or_create(
                        product=product,
                        point=to_point,
                        defaults={'quantity': 0}
                    )

                    # Обновляем остатки
                    from_inv.quantity -= quantity
                    from_inv.save()

                    to_inv.quantity += quantity
                    to_inv.save()

                    # Создаём запись в истории
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
    inventories = PointInventory.objects.select_related('product', 'point').all()
    return render(request, 'inventory/inventory_list.html', {'inventories': inventories})


def inventory_detail_view(request, inventory_id):
    inventory = PointInventory.objects.get(id=inventory_id)
    movements = StockMovement.objects.filter(product_inventory=inventory).order_by('-timestamp')
    return render(request, 'inventory/inventory_detail.html', {
        'inventory': inventory,
        'movements': movements
    })


@user_passes_test(lambda u: u.is_superuser or u.is_staff or u.groups.filter(name='Модераторы').exists())
def add_inventory(request):
    if request.method == 'POST':
        form = PointInventoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventory:inventory_list')
    else:
        form = PointInventoryForm()

    return render(request, 'inventory/add_inventory.html', {'form': form})

def stock_movement_history(request):
    movements = StockMovement.objects.select_related('from_point', 'to_point').all().order_by('-timestamp')
    return render(request, 'inventory/history.html', {'movements': movements})


def low_stock_alert(request):
    threshold = 5  # или получать из GET параметра
    inventories = PointInventory.objects.filter(quantity__lt=threshold)
    return render(request, 'inventory/low_stock.html', {'inventories': inventories})


def stock_history(request):
    movements = StockMovement.objects.select_related(
        'product_inventory',
        'from_point',
        'to_point'
    ).all().order_by('-timestamp')

    return render(request, 'inventory/history.html', {
        'movements': movements
    })
