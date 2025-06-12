# pos/admin.py

from django.contrib import admin
from .models import Point


@admin.register(Point)
class PointAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'manager')
    search_fields = ('name', 'address')
    list_filter = ('is_active',)


    @admin.action(description='Активировать выбранные пункты')
    def activate_points(self, request, queryset):
        queryset.update(is_active=True)


    @admin.action(description='Деактивировать выбранные пункты')
    def deactivate_points(self, queryset):
        queryset.update(is_active=False)
