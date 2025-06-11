# orders/admin.py

from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price', 'total')
    fields = ('product', 'quantity', 'price', 'total')

    @admin.display(description='Сумма')
    def total(self, obj):
        return obj.total


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'name',
        'phone',
        'delivery_type',
        'payment_type',
        'status',
        'total_price',
        'created_at'
    )
    list_filter = ('status', 'delivery_type', 'payment_type', 'created_at')
    search_fields = ('name', 'phone', 'address', 'user__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'total_price')
    inlines = [OrderItemInline]

    fieldsets = (
        (None, {
            'fields': ('user', 'name', 'phone', 'email', 'address')
        }),
        ('Доставка и оплата', {
            'fields': ('delivery_type', 'payment_type', 'status')
        }),
        ('Дополнительно', {
            'fields': ('total_price', 'created_at')
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'total')
    list_filter = ('order', 'product')
    search_fields = ('order__id', 'product__name')

    @admin.display(description='Сумма')
    def total(self, obj):
        return obj.quantity * obj.price