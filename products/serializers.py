# products/serializers.py

from rest_framework import serializers
from .models import Product, Category, ProductAttribute, ProductAttributeValue, ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    """
    Сериализатор изображений товара
    """
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_main', 'created_at']


class ProductAttributeValueSerializer(serializers.ModelSerializer):
    """
    Сериализатор значений атрибутов
    """
    attribute_name = serializers.CharField(source='attribute.name', read_only=True)

    class Meta:
        model = ProductAttributeValue
        fields = ['id', 'attribute', 'attribute_name', 'value']


class ProductListSerializer(serializers.ModelSerializer):
    """
    Для вывода списка товаров
    """
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'category', 'category_name', 'is_active']
        read_only_fields = ['id']


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Детали товара: описание, изображения, атрибуты
    """
    attributes = ProductAttributeValueSerializer(many=True, source='attributes.all')
    images = ProductImageSerializer(many=True, source='images.all')
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id',
            'name',
            'description',
            'price',
            'category',
            'category_name',
            'attributes',
            'images',
            'is_active',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор категории
    """
    parent_category = serializers.CharField(
        source='parent.name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = Category
        fields = ['id', 'name', 'parent', 'parent_category']
        read_only_fields = ['id']


class ProductAttributeSerializer(serializers.ModelSerializer):
    """
    Атрибуты товаров (например: цвет, размер)
    """
    class Meta:
        model = ProductAttribute
        fields = ['id', 'name']
        read_only_fields = ['id']


class ProductAttributeValueSerializer(serializers.ModelSerializer):
    """
    Значения атрибутов
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    attribute_name = serializers.CharField(source='attribute.name', read_only=True)

    class Meta:
        model = ProductAttributeValue
        fields = ['id', 'product', 'product_name', 'attribute', 'attribute_name', 'value']
        read_only_fields = ['id']
