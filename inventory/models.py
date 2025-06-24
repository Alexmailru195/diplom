# inventory/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from pos.models import Point
from products.models import Product


class PointInventory(models.Model):
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        verbose_name=_("Товар")
    )
    point = models.ForeignKey(
        'pos.Point',
        on_delete=models.CASCADE,
        verbose_name=_("Пункт выдачи")
    )
    quantity = models.PositiveIntegerField(default=0, verbose_name=_("Количество"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))

    def save(self, *args, **kwargs):
        try:
            prev = PointInventory.objects.get(pk=self.pk)
            if self.quantity > prev.quantity:
                added = self.quantity - prev.quantity
                # Записываем только добавление
                StockHistory.objects.create(
                    product=self.product,
                    point_to=self.point,
                    quantity=added,
                    action='add',
                    comment=f"Добавлено {added} шт. товара '{self.product.name}' на '{self.point.name}'."
                )
            elif self.quantity < prev.quantity:
                removed = prev.quantity - self.quantity
                # Записываем только списание
                StockHistory.objects.create(
                    product=self.product,
                    point_from=self.point,
                    quantity=removed,
                    action='sale',
                    comment=f"Списано {removed} шт. товара '{self.product.name}' с '{self.point.name}'."
                )

        except PointInventory.DoesNotExist:
            pass  # Новая запись — можно не логировать

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} — {self.point.name}, {self.quantity} шт."

    class Meta:
        verbose_name = "Остаток на точке"
        verbose_name_plural = "Остатки на точках"
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'point'],
                name='unique_product_point'
            )
        ]


class StockMovement(models.Model):
    MOVEMENT_TYPES = (
        ('in', 'Приход'),
        ('out', 'Расход'),
        ('move', 'Перемещение')
    )

    movement_type = models.CharField(
        max_length=10,
        choices=MOVEMENT_TYPES,
        null=False,
        blank=False,
    )

    product_inventory = models.ForeignKey(
        'PointInventory',
        on_delete=models.CASCADE,
        verbose_name="Инвентарь"
    )
    from_point = models.ForeignKey(
        Point,
        on_delete=models.SET_NULL,
        null=True,
        related_name='movement_out'
    )
    to_point = models.ForeignKey(
        Point,
        on_delete=models.SET_NULL,
        null=True,
        related_name='movement_in'
    )
    quantity = models.PositiveIntegerField("Количество")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} шт. из {self.from_point} в {self.to_point}"


class StockHistory(models.Model):
    ACTION_CHOICES = (
        ('sale', 'Списание'),
        ('move', 'Перемещение'),
        ('add', 'Добавление'),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    point_from = models.ForeignKey(
        Point,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_history_out'
    )
    point_to = models.ForeignKey(
        Point,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_history_in'
    )
    quantity = models.PositiveIntegerField(default=0)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.get_action_display()}"

    class Meta:
        verbose_name = "История инвентаря"
        verbose_name_plural = "История инвентаря"
