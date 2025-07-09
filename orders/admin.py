# orders/admin.py

from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """
    Inline-админка для отображения позиций заказа (OrderItem) внутри модели Order.
    Позволяет просматривать товары и их стоимость без возможности редактирования.
    """

    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price', 'total')
    fields = ('product', 'quantity', 'price', 'total')

    @admin.display(description='Сумма')
    def total(self, obj):
        return obj.quantity * obj.price


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Административная панель для управления моделью Order.
    Отображает список заказов, фильтрацию по статусу, типу доставки и оплаты,
    а также ограничивает доступ к заказам только менеджерам или администраторам.
    """

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
        Возвращает набор заказов, который будет виден в административной панели.
        Для суперпользователей — все заказы. Для менеджеров — только те заказы,
        которые назначены им.

        Args:
            request: Объект запроса Django.

        Returns:
            QuerySet: Список заказов, доступных пользователю.
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        else:
            return qs.filter(manager=request.user)

    def has_change_permission(self, request, obj=None):
        """
        Определяет, имеет ли пользователь право на изменение заказа.
        Право предоставляется только менеджеру заказа или администратору.

        Args:
            request: Объект запроса Django.
            obj: Объект заказа.

        Returns:
            bool: True, если у пользователя есть права на изменение.
        """
        if not request.user.is_superuser and obj and obj.manager != request.user:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """
        Определяет, имеет ли пользователь право на удаление заказа.
        Право предоставляется только менеджеру заказа или администратору.

        Args:
            request: Объект запроса Django.
            obj: Объект заказа.

        Returns:
            bool: True, если у пользователя есть права на удаление.
        """
        if not request.user.is_superuser and obj and obj.manager != request.user:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """
    Административная панель для управления моделью OrderItem.
    Отображает товары в заказе, их количество, цену и общую сумму.
    """

    list_display = ('order', 'product', 'quantity', 'price', 'total')
    list_filter = ('order', 'product')
    search_fields = ('order__id', 'product__name')

    @admin.display(description='Сумма')
    def total(self, obj):
        return obj.quantity * obj.price
