# pos/views.py
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, get_object_or_404, redirect

from inventory.models import PointInventory
from users.decorators import permission_required
from .models import Point
from .forms import PointForm


def is_manager(user):
    return user.is_superuser or user.groups.filter(name='Менеджеры точек').exists()


@permission_required
def point_list_view(request):
    points = Point.objects.all()
    return render(request, 'pos/point_list.html', {'points': points})


@user_passes_test(is_manager)
def point_detail_view(request, point_id):
    point = get_object_or_404(Point, id=point_id)
    inventories = PointInventory.objects.filter(point=point).select_related('product')
    return render(request, 'pos/point_detail.html', {
        'point': point,
        'inventories': inventories
    })


def point_create_view(request):
    if request.method == 'POST':
        form = PointForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pos:point_list')
    else:
        form = PointForm()

    return render(request, 'pos/point_form.html', {'form': form})


def point_update_view(request, point_id):
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
    point = get_object_or_404(Point, id=point_id)
    if request.method == 'POST':
        point.delete()
        return redirect('pos:point_list')

    return render(request, 'pos/point_confirm_delete.html', {'point': point})