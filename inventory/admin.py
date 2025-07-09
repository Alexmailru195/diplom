# inventory/admin.py

from django.contrib import admin
from .models import PointInventory, StockMovement


@admin.register(PointInventory)
class PointInventoryAdmin(admin.ModelAdmin):
    """
    Административная панель для управления моделью PointInventory.
    Позволяет просматривать, фильтровать и искать остатки товаров на разных точках.
    """

    list_display = ('product', 'point', 'quantity', 'updated_at')
    search_fields = ('product__name', 'point__name')
    list_filter = ('point', 'product')


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    """
    Административная панель для модели StockMovement.
    Отображает историю перемещений товаров между точками.
    """

    list_display = ('timestamp', 'product_name', 'from_point', 'to_point', 'quantity')
    list_filter = ('product_inventory__product', 'from_point', 'to_point')

    def product_name(self, obj):
        """
        Возвращает имя товара из связанной модели Product через PointInventory.

        Args:
            obj (StockMovement): Объект истории перемещения.

        Returns:
            str: Название товара или None, если товар не найден.
        """
        return obj.product_inventory.product.name if obj.product_inventory else None

    product_name.short_description = 'Товар'
    product_name.admin_order_field = 'product_inventory__product'
