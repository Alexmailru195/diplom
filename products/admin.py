# products/admin.py

from django.contrib import admin
from .models import Product, Category, ProductAttribute, ProductAttributeValue, ProductImage


class ProductImageInline(admin.TabularInline):
    """
    Inline-админка для отображения изображений товаров внутри модели Product.
    Позволяет добавлять и просматривать изображения без отдельного перехода к модели ProductImage.
    """

    model = ProductImage
    extra = 1
    readonly_fields = ('is_main',)
    verbose_name = "Изображение товара"
    verbose_name_plural = "Изображения товаров"


class ProductAttributeValueInline(admin.TabularInline):
    """
    Inline-админка для отображения атрибутов товаров внутри модели Product.
    Позволяет добавлять и редактировать атрибуты на странице редактирования товара.
    """

    model = ProductAttributeValue
    extra = 1
    verbose_name = "Атрибут"
    verbose_name_plural = "Атрибуты товара"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Административная панель для управления моделью Product.
    Отображает название, цену, категорию, список атрибутов и изображений.
    """

    list_display = ('name', 'price', 'category', 'get_attributes')
    list_filter = ('category',)
    search_fields = ('name', 'description', 'category__name')
    inlines = [ProductAttributeValueInline, ProductImageInline]
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'price', 'category', 'is_active')
        }),
        ('Дополнительно', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)

    def get_attributes(self, obj):
        """Формирует строку с атрибутами товара."""
        return ", ".join(f"{attr.attribute.name}: {attr.value}" for attr in obj.attributes.all())
    get_attributes.short_description = 'Атрибуты'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Административная панель для управления моделью Category.
    Отображает имя категории, родительскую категорию и количество товаров в категории.
    """

    list_display = ('name', 'parent', 'product_count')
    list_filter = ('parent',)
    search_fields = ('name',)
    ordering = ('name',)
    prepopulated_fields = {'name': ('name',)}
    fieldsets = (
        (None, {
            'fields': ('name', 'parent')
        }),
    )

    def product_count(self, obj):
        """Возвращает количество товаров в данной категории."""
        return obj.products.count()
    product_count.short_description = "Кол-во товаров"


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    """
    Административная панель для управления моделью ProductAttribute.
    Отображает доступные атрибуты и позволяет фильтровать по названию.
    """

    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
    prepopulated_fields = {'name': ('name',)}


@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    """
    Административная панель для управления моделью ProductAttributeValue.
    Отображает связь между продуктом, атрибутом и его значением.
    """

    list_display = ('product', 'attribute', 'value')
    list_filter = ('attribute', 'product')
    search_fields = ('product__name', 'attribute__name')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    """
    Административная панель для управления моделью ProductImage.
    Отображает изображения товаров, указывает, является ли оно главным.
    """

    list_display = ('product', 'image', 'is_main')
    list_filter = ('is_main',)
    search_fields = ('product__name',)
    readonly_fields = ('created_at',)
