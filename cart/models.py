# cart/models.py

from django.db import models
from django.conf import settings
from products.models import Product


class Cart(models.Model):
    """
    Модель корзины пользователя.
    Каждый пользователь имеет только одну корзину, которая хранит список добавленных товаров.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name="Пользователь"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Корзина {self.user.username}"

    @property
    def total_price(self):
        """
        Считает общую стоимость всех товаров в корзине.

        Returns:
            float: Общая сумма заказа.
        """
        return sum(item.total for item in self.items.all())

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"


class CartItem(models.Model):
    """
    Позиция товара в корзине.
    Хранит информацию о количестве и цене конкретного товара в корзине.
    """

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="Корзина"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="Товар"
    )
    quantity = models.PositiveIntegerField("Количество", default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    @property
    def total(self):
        """
        Рассчитывает стоимость одного товара с учётом количества.

        Returns:
            float: Общая цена указанного количества товара.
        """
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name} × {self.quantity}"

    class Meta:
        verbose_name = "Позиция корзины"
        verbose_name_plural = "Позиции корзин"


class GuestCart(models.Model):
    """
    Гостевая корзина.
    Используется для временного хранения товаров неавторизованных пользователей.
    """

    session_key = models.CharField(max_length=40)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Гостевая позиция {self.product.name} x {self.quantity}"

    class Meta:
        unique_together = ('session_key', 'product')
