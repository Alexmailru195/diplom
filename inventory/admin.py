# inventory/admin.py

from django.contrib import admin
from .models import ProductInventory, StockMovement


class StockMovementInline(admin.TabularInline):
    """
    Inline для отображения движений товара внутри карточки инвентаря
    """
    model = StockMovement
    extra = 0
    readonly_fields = ('movement_type', 'quantity', 'timestamp', 'related_order')
    can_delete = False
    can_add_related = False
    verbose_name = "Движение товара"
    verbose_name_plural = "Движения товаров"


@admin.register(ProductInventory)
class ProductInventoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'updated_at')
    search_fields = ('product__name',)
    list_filter = ('quantity', 'updated_at')
    inlines = [StockMovementInline]
    readonly_fields = ('updated_at',)
    ordering = ('-updated_at',)

    fieldsets = (
        ('Информация о товаре', {
            'fields': ('product', 'quantity', 'updated_at')
        }),
    )

    def save_model(self, request, obj, form, change):
        # При сохранении обновляем время
        obj.save()
        super().save_model(request, obj, form, change)


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('product_inventory', 'movement_type', 'quantity', 'timestamp', 'related_order')
    list_filter = ('movement_type', 'timestamp')
    search_fields = ('product_inventory__product__name',)
    readonly_fields = ('timestamp', 'related_order')

    fieldsets = (
        ('Детали движения', {
            'fields': ('product_inventory', 'movement_type', 'quantity', 'related_order', 'timestamp')
        }),
    )

    ordering = ('-timestamp',)