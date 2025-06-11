# inventory/models.py

from django.db import models
from products.models import Product
from orders.models import Order


class ProductInventory(models.Model):
    """
    Остатки товара на складе
    """
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name='inventory',
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField(default=0, verbose_name='Количество')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлено')

    def __str__(self):
        return f"{self.product.name} — {self.quantity} шт."

    class Meta:
        verbose_name = "Остаток товара"
        verbose_name_plural = "Инвентарь товаров"
        ordering = ['-updated_at']


class StockMovement(models.Model):
    """
    Лог движения остатков (приход/расход)
    """
    MOVEMENT_TYPES = (
        ('in', 'Приход'),
        ('out', 'Расход'),
        ('adjust', 'Коррекция'),
    )

    product_inventory = models.ForeignKey(
        ProductInventory,
        on_delete=models.CASCADE,
        related_name='movements',
        verbose_name='Инвентарь'
    )
    movement_type = models.CharField(
        max_length=10,
        choices=MOVEMENT_TYPES,
        verbose_name='Тип движения'
    )
    quantity = models.IntegerField(verbose_name='Количество')
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name='Дата')
    related_order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Связанный заказ'
    )
    description = models.TextField(blank=True, null=True, verbose_name='Описание')

    def __str__(self):
        return f"{self.get_movement_type_display()} | {self.product_inventory.product.name} — {self.quantity} шт."

    class Meta:
        verbose_name = "Движение товара"
        verbose_name_plural = "Движения товаров"
        ordering = ['-timestamp']
