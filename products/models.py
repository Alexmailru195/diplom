# products/models.py

from django.db import models


class Category(models.Model):
    """
    Модель категории товаров.
    Категории могут быть вложенными (через поле parent).
    Позволяет группировать товары и отображать их по категориям.
    """

    name = models.CharField("Название", max_length=100)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subcategories',
        verbose_name="Родительская категория"
    )

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        """Возвращает полное имя категории с учётом родительской категории."""
        if self.parent:
            return f"{self.parent.get_full_name()} > {self.name}"
        return self.name

    def get_all_products(self):
        """
        Возвращает все товары, принадлежащие данной категории и её подкатегориям.

        Returns:
            QuerySet: Список товаров.
        """
        from .models import Product

        products = Product.objects.filter(category=self)

        return products.distinct()

    def get_product_count(self):
        """
        Возвращает количество товаров в текущей категории и её подкатегориях.

        Returns:
            int: Общее количество товаров.
        """
        return self.get_all_products().count()

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']


class Product(models.Model):
    """
    Модель товара.
    Хранит информацию о названии, описании, цене, статусе активности и популярности.
    """

    name = models.CharField("Название", max_length=255)
    description = models.TextField("Описание")
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Категория",
        related_name='products'
    )
    is_active = models.BooleanField("Активный", default=True)
    is_popular = models.BooleanField("Популярный", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']


class ProductAttribute(models.Model):
    """
    Модель атрибута товара.
    Используется для хранения общих характеристик, которые могут применяться к разным товарам.
    """

    name = models.CharField("Название атрибута", max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Атрибут товара"
        verbose_name_plural = "Атрибуты товаров"


class ProductAttributeValue(models.Model):
    """
    Значение атрибута конкретного товара.
    Связывает товар с его атрибутом и указывает значение этого атрибута.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='attributes'
    )
    attribute = models.ForeignKey(
        ProductAttribute,
        on_delete=models.CASCADE
    )
    value = models.CharField("Значение", max_length=255)

    def __str__(self):
        return f"{self.product} | {self.attribute}: {self.value}"

    class Meta:
        verbose_name = "Значение атрибута"
        verbose_name_plural = "Значения атрибутов"


class ProductImage(models.Model):
    """
    Модель изображений товаров.
    Позволяет добавлять несколько изображений к одному товару.
    Только одно изображение может быть основным.
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField("Изображение", upload_to='product_images/')
    is_main = models.BooleanField("Основное изображение", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Изображение: {self.product.name}"

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"

    def save(self, *args, **kwargs):
        """
        Перед сохранением убедиться, что только одно изображение может быть основным у одного товара.
        Если текущее изображение помечено как основное, остальные становятся неосновными.
        """
        if self.is_main:
            ProductImage.objects.filter(product=self.product).exclude(pk=self.pk).update(is_main=False)
        super().save(*args, **kwargs)
