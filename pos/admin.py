# pos/admin.py

from django.contrib import admin
from .models import Point


@admin.register(Point)
class PointAdmin(admin.ModelAdmin):
    """
    Административная панель для управления моделью Point.
    Отображает список пунктов выдачи, позволяет фильтровать и искать по названию и адресу.
    """

    list_display = ('name', 'address', 'manager')
    search_fields = ('name', 'address')
    list_filter = ('is_active',)


@admin.action(description='Активировать выбранные пункты')
def activate_points(self, request, queryset):
    """
    Админ-действие: активирует выбранные пункты выдачи.
    Устанавливает поле is_active в True для всех выбранных объектов.
    """
    queryset.update(is_active=True)


@admin.action(description='Деактивировать выбранные пункты')
def deactivate_points(self, request, queryset):
    """
    Админ-действие: деактивирует выбранные пункты выдачи.
    Устанавливает поле is_active в False для всех выбранных объектов.
    """
    queryset.update(is_active=False)
