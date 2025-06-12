# orders/models.py

from django.db import models
from django.conf import settings
from products.models import Product
from pos.models import Point


class Order(models.Model):
    DELIVERY_CHOICES = (
        ('courier', 'Доставка'),
        ('pickup', 'Самовывоз'),
    )

    PAYMENT_CHOICES = (
        ('online', 'Онлайн'),
        ('cash', 'Наличные при получении'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    delivery_type = models.CharField(max_length=10, choices=DELIVERY_CHOICES)
    pickup_point = models.ForeignKey(Point, on_delete=models.SET_NULL, null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    delivery_time = models.TimeField(null=True, blank=True)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    status = models.CharField(max_length=20, default='created')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Заказ #{self.id} от {self.name}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.product.name} × {self.quantity}"