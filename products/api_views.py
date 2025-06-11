# products/api_views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Product, Category, ProductAttribute, ProductAttributeValue
from .serializers import (
    ProductListSerializer,
    CategorySerializer,
    ProductAttributeSerializer,
    ProductDetailSerializer
)


class ProductListView(APIView):
    """
    Получить список всех товаров с возможностью фильтрации
    Пример URL: /api/products/
    """
    def get(self, request):
        category_id = request.query_params.get('category')
        attribute_id = request.query_params.get('attribute')
        search_query = request.query_params.get('search')

        products = Product.objects.all()

        if category_id:
            try:
                category = Category.objects.get(id=category_id)
                products = products.filter(category=category)
            except Category.DoesNotExist:
                return Response(
                    {"detail": "Категория не найдена"},
                    status=status.HTTP_404_NOT_FOUND
                )

        if attribute_id:
            try:
                attribute = ProductAttribute.objects.get(id=attribute_id)
                product_ids = ProductAttributeValue.objects.filter(
                    attribute=attribute
                ).values_list('product', flat=True)
                products = products.filter(id__in=product_ids)
            except ProductAttribute.DoesNotExist:
                return Response(
                    {"detail": "Атрибут не найден"},
                    status=status.HTTP_404_NOT_FOUND
                )

        if search_query:
            products = products.filter(name__icontains=search_query)

        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class ProductDetailView(APIView):
    """
    Получить детальную информацию о товаре
    Пример URL: /api/products/1/
    """
    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductDetailSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({"detail": "Товар не найден"}, status=status.HTTP_404_NOT_FOUND)


class CategoryListView(APIView):
    """
    Получить список всех категорий
    """
    def get(self, request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


class CategoryProductListView(APIView):
    """
    Получить товары из определённой категории
    Пример URL: /api/categories/2/products/
    """
    def get(self, request, category_pk):
        try:
            category = Category.objects.get(pk=category_pk)
        except Category.DoesNotExist:
            return Response({"detail": "Категория не найдена"}, status=status.HTTP_404_NOT_FOUND)

        products = Product.objects.filter(category=category)
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class ProductAttributeListView(APIView):
    """
    Получить все доступные атрибуты
    """
    def get(self, request):
        attributes = ProductAttribute.objects.all()
        serializer = ProductAttributeSerializer(attributes, many=True)
        return Response(serializer.data)


class ProductAttributeValueListView(APIView):
    """
    Получить значения атрибутов для конкретного товара
    Пример: /api/products/1/attributes/
    """
    def get(self, request, product_pk):
        try:
            product = Product.objects.get(pk=product_pk)
        except Product.DoesNotExist:
            return Response({"detail": "Товар не найден"}, status=status.HTTP_404_NOT_FOUND)

        attributes = ProductAttributeValue.objects.filter(product=product)
        data = {
            attr.attribute.name: attr.value for attr in attributes
        }
        return Response(data)