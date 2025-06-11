# cart/admin.py

from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('product', 'quantity')
    can_delete = False
    verbose_name = "Позиция корзины"
    verbose_name_plural = "Позиции корзины"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'item_count', 'total_price')
    inlines = [CartItemInline]
    search_fields = ('user__username',)
    ordering = ('-created_at',)

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = "Число товаров"

    def total_price(self, obj):
        return sum(item.total_price for item in obj.items.all())
    total_price.short_description = "Итоговая сумма"