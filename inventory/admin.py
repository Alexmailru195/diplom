from django.contrib import admin
from .models import Warehouse, Inventory


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'is_active')
    search_fields = ('name', 'address')
    list_filter = ('is_active',)
    ordering = ('-is_active', 'name')


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('warehouse', 'product', 'stock', 'reserved', 'updated_at')
    search_fields = ('product__name', 'warehouse__name')
    list_filter = ('warehouse', 'product')
    ordering = ('-updated_at',)
