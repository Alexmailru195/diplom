# products/models.py

from django.db import models


class Category(models.Model):
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
        if self.parent:
            return f"{self.parent.get_full_name()} > {self.name}"
        return self.name

    def get_all_products(self):
        from .models import Product

        products = Product.objects.filter(category=self)

        return products.distinct()

    def get_product_count(self):
        """Получить количество товаров в текущей категории и её подкатегориях"""
        return self.get_all_products().count()

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']


class Product(models.Model):
    name = models.CharField("Название", max_length=255)
    description = models.TextField("Описание")
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Категория",
        related_name = 'products'
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
    name = models.CharField("Название атрибута", max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Атрибут товара"
        verbose_name_plural = "Атрибуты товаров"


class ProductAttributeValue(models.Model):
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
        # Убедимся, что только одно изображение может быть основным у товара
        if self.is_main:
            ProductImage.objects.filter(product=self.product).exclude(pk=self.pk).update(is_main=False)
        super().save(*args, **kwargs)