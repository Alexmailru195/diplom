# pos/admin.py

from django.contrib import admin
from .models import SalesPoint, PointInventory, Sale


class PointInventoryInline(admin.TabularInline):
    model = PointInventory
    extra = 0
    readonly_fields = ('product', 'quantity')
    can_delete = False
    verbose_name = "Остаток товара"
    verbose_name_plural = "Остатки товаров"


@admin.register(SalesPoint)
class SalesPointAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'manager', 'created_at')
    search_fields = ('name', 'address', 'manager__username')
    list_filter = ('created_at',)
    inlines = [PointInventoryInline]
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'address', 'manager')
        }),
        ('Дополнительно', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(PointInventory)
class PointInventoryAdmin(admin.ModelAdmin):
    list_display = ('sales_point', 'product', 'quantity', 'updated_at')
    list_filter = ('sales_point', 'product')
    search_fields = ('sales_point__name', 'product__name')
    readonly_fields = ('updated_at',)
    fieldsets = (
        ('Точка продаж', {
            'fields': ('sales_point',)
        }),
        ('Товар', {
            'fields': ('product', 'quantity')
        }),
        ('Информация', {
            'fields': ('updated_at',)
        }),
    )

    def has_add_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    def save_model(self, request, obj, form, change):
        if not change:
            # Автоматически установить менеджера из User
            pass
        super().save_model(request, obj, form, change)


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('sales_point', 'product', 'quantity', 'total_price', 'sale_date', 'user')
    list_filter = ('sale_date', 'sales_point', 'user')
    search_fields = ('product__name', 'sales_point__name')

    def total_price(self, obj):
        return obj.product.price * obj.quantity
    total_price.short_description = 'Сумма'

    def has_add_permission(self, request):
        return False  # Запретить добавление вручную

    def has_change_permission(self, request, obj=None):
        return False  # Запретить редактирование

    def has_delete_permission(self, request, obj=None):
        return False  # Запретить удаление

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'sales_point', 'user')