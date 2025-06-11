from django.db import models
from products.models import Product


class Warehouse(models.Model):
    """Склад или торговая точка"""
    name = models.CharField('Название', max_length=255)
    address = models.TextField('Адрес')
    is_active = models.BooleanField('Активен', default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Склад / Точка'
        verbose_name_plural = 'Склады и точки'


class Inventory(models.Model):
    """Остатки товара на складе"""
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, verbose_name='Склад')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар')
    stock = models.PositiveIntegerField('Количество на складе', default=0)
    reserved = models.PositiveIntegerField('Зарезервировано', default=0)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    def __str__(self):
        return f"{self.product} | {self.warehouse}: {self.stock}"

    class Meta:
        unique_together = ('warehouse', 'product')
        verbose_name = 'Остаток'
        verbose_name_plural = 'Остатки'
