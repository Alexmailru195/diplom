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
        return obj.quantity * obj.price


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

    def get_queryset(self, request):
        """
        Показываем только те заказы, которые назначены менеджеру точки.
        Если пользователь — суперпользователь, показываем все.
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(manager=request.user)

    def has_change_permission(self, request, obj=None):
        """
        Позволяем редактировать заказ только его менеджеру или администратору.
        """
        if not request.user.is_superuser and obj and obj.manager != request.user:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """
        Позволяем удалять заказ только его менеджеру или администратору.
        """
        if not request.user.is_superuser and obj and obj.manager != request.user:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price', 'total')
    list_filter = ('order', 'product')
    search_fields = ('order__id', 'product__name')

    @admin.display(description='Сумма')
    def total(self, obj):
        return obj.quantity * obj.price
