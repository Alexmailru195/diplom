# inventory/admin.py

from django.contrib import admin
from .models import PointInventory, StockMovement


@admin.register(PointInventory)
class PointInventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'point', 'quantity', 'updated_at')
    search_fields = ('product__name', 'point__name')
    list_filter = ('point', 'product')


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'product_name', 'from_point', 'to_point', 'quantity')
    list_filter = ('product_inventory__product', 'from_point', 'to_point')

    def product_name(self, obj):
        return obj.product_inventory.product.name if obj.product_inventory else None

    product_name.short_description = 'Товар'
    product_name.admin_order_field = 'product_inventory__product'
