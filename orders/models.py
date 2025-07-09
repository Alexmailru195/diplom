# orders/models.py

from django.db import models
from django.conf import settings
from products.models import Product
from pos.models import Point


class Order(models.Model):
    """
    Модель заказа.
    Содержит информацию о клиенте, способах доставки и оплаты, статусе заказа и общей сумме.
    """

    DELIVERY_CHOICES = (
        ('courier', 'Доставка'),
        ('pickup', 'Самовывоз'),
    )

    PAYMENT_CHOICES = (
        ('online', 'Онлайн'),
        ('cash', 'Наличные/безналичные при получении'),
    )

    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('failed', 'Неоплачен'),
    )

    TIME_SLOT_CHOICES = (
        ('morning', 'Утро (9:00–13:00)'),
        ('afternoon', 'День (13:00–17:00)'),
    )

    STATUS_CHOICES = (
        ('created', 'Создан'),
        ('accepted', 'Принят'),
        ('collected', 'Собран'),
        ('sent', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders_as_manager'
    )
    name = models.CharField(max_length=100, verbose_name="Имя")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    address = models.TextField(blank=True, null=True, verbose_name="Адрес доставки")
    delivery_type = models.CharField(max_length=10, choices=DELIVERY_CHOICES, verbose_name="Тип доставки")
    pickup_point = models.ForeignKey(Point, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders', verbose_name="Пункт самовывоза")
    delivery_date = models.DateField(null=True, blank=True, verbose_name="Дата доставки")
    time_slot = models.CharField(max_length=10, choices=TIME_SLOT_CHOICES, blank=True, null=True, verbose_name="Время доставки")
    payment_type = models.CharField(
        max_length=10,
        choices=PAYMENT_CHOICES,
        verbose_name="Способ оплаты",
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='pending'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Итоговая сумма")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Заказ #{self.id} от {self.name}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class OrderItem(models.Model):
    """
    Позиция товара в заказе.
    Хранит информацию о товаре, количестве, цене и общей стоимости позиции.
    """

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name="Продукт")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")

    @property
    def total(self):
        """Рассчитывает общую стоимость одного товара с учётом количества."""
        return self.quantity * self.price

    def __str__(self):
        return f"{self.product.name} x {self.quantity} — Заказ №{self.order.id}"

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказов"
