# orders/models.py

from django.db import models
from django.conf import settings
from products.models import Product


class Order(models.Model):
    """
    Модель заказа пользователя
    """

    STATUS_CHOICES = (
        ('created', 'Создан'),
        ('paid', 'Оплачен'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('completed', 'Завершён'),
        ('cancelled', 'Отменён'),
    )

    DELIVERY_CHOICES = (
        ('courier', 'Курьер'),
        ('pickup', 'Самовывоз'),
    )

    PICKUP_POINTS = (
        ('point1', 'ул. Ленина, д. 10 (Пункт выдачи)'),
        ('point2', 'ул. Гагарина, д. 5 (Пункт выдачи)'),
        ('point3', 'Москва, ТЦ Центральный (Пункт выдачи)'),
    )

    pickup_point = models.CharField(
        "Пункт самовывоза",
        max_length=100,
        choices=PICKUP_POINTS,
        blank=True,
        null=True
    )

    delivery_date = models.DateField("Дата доставки", blank=True, null=True)
    delivery_time = models.TimeField("Время доставки", blank=True, null=True)

    PAYMENT_CHOICES = (
        ('online', 'Онлайн'),
        ('cash', 'Наличные при получении'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='orders',
        blank=True,
        null=True,
        verbose_name='Пользователь'
    )
    name = models.CharField('Имя', max_length=100)
    phone = models.CharField('Телефон', max_length=20, blank=True, null=True)
    email = models.EmailField('Email', blank=True, null=True)
    address = models.TextField('Адрес доставки', blank=True, null=True)
    delivery_type = models.CharField(
        'Способ доставки',
        max_length=20,
        choices=DELIVERY_CHOICES,
        default='courier',
    )
    payment_type = models.CharField(
        'Способ оплаты',
        max_length=20,
        choices=PAYMENT_CHOICES,
        default='online',
    )
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default='created',
    )
    total_price = models.DecimalField(
        'Итого',
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    def get_email(self):
        # Берём email пользователя или из формы
        return self.email or (self.user.email if self.user else None)

    def __str__(self):
        return f"Заказ #{self.id} от {self.name}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class OrderItem(models.Model):
    """
    Позиции в заказе
    """

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заказ'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField('Количество', default=1)
    price = models.DecimalField('Цена за единицу', max_digits=10, decimal_places=2)

    @property
    def total(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.product.name} × {self.quantity}"

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказов"
