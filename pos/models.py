# pos/models.py

from django.db import models
from products.models import Product
from users.models import User
from inventory.models import ProductInventory


class SalesPoint(models.Model):
    """
    Точка продаж (POS)
    Например: магазин, пункт выдачи
    """
    name = models.CharField("Название точки", max_length=255)
    address = models.TextField("Адрес")
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role__in': ['manager', 'admin']},
        verbose_name="Менеджер точки"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Точка продаж"
        verbose_name_plural = "Точки продаж"


class PointInventory(models.Model):
    """
    Остатки товаров в точке продаж
    """
    sales_point = models.ForeignKey(
        SalesPoint,
        on_delete=models.CASCADE,
        related_name='inventory'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField("Количество", default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.sales_point} — {self.product.name}"

    class Meta:
        verbose_name = "Остаток в точке"
        verbose_name_plural = "Остатки в точках"
        unique_together = ('sales_point', 'product')


class Sale(models.Model):
    """
    Продажа через POS
    """
    sales_point = models.ForeignKey(
        SalesPoint,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Точка продаж"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Товар"
    )
    quantity = models.PositiveIntegerField("Количество")
    sale_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата продажи")
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Продавец"
    )

    def __str__(self):
        return f"Продажа: {self.product.name} x {self.quantity}"

    @property
    def total_price(self):
        return self.product.price * self.quantity if self.product else 0

    class Meta:
        verbose_name = "Продажа"
        verbose_name_plural = "Продажи"
        ordering = ['-sale_date']