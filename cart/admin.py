# cart/admin.py

from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    """
    Inline-админка для отображения позиций корзины внутри модели Cart.
    Позволяет просматривать товары в корзине без возможности их редактирования или удаления.
    """
    model = CartItem
    extra = 0
    readonly_fields = ('product', 'quantity')
    can_delete = False
    verbose_name = "Позиция корзины"
    verbose_name_plural = "Позиции корзины"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """
    Административная панель для управления корзинами пользователей.
    Отображает пользователя, количество товаров и общую сумму заказа.
    """

    list_display = ('user', 'item_count', 'total_price')
    inlines = [CartItemInline]
    search_fields = ('user__username',)
    ordering = ('-created_at',)

    def item_count(self, obj):
        """
        Возвращает количество товаров в корзине.
        """
        return obj.items.count()
    item_count.short_description = "Число товаров"

    def total_price(self, obj):
        """
        Возвращает общую стоимость товаров в корзине.
        """
        return sum(item.total for item in obj.items.all())
    total_price.short_description = "Итоговая сумма"
