# products/views.py

from django.shortcuts import render, get_object_or_404

from .models import Product, Category
from django.db.models import Count


def product_list_view(request):
    # Получаем все товары
    products = Product.objects.all()

    # Аннотируем количество товаров в каждой категории
    categories = Category.objects.annotate(product_count=Count('products'))

    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories
    })


def product_detail_view(request, pk):
    """
    Детали товара: описание, атрибуты, изображения
    """
    product = get_object_or_404(Product, pk=pk, is_active=True)
    attributes = product.attributes.all()  # через related_name='attributes'
    images = product.images.all()

    context = {
        'product': product,
        'attributes': attributes,
        'images': images
    }

    return render(request, 'products/product_detail.html', context)


def category_product_list_view(request, category_pk):
    """
    Список товаров в определённой категории
    """
    category = get_object_or_404(Category, pk=category_pk)
    products = Product.objects.filter(category=category, is_active=True)
    categories = Category.objects.all()

    context = {
        'products': products,
        'current_category': category,
        'categories': categories
    }

    return render(request, 'products/category_products.html', context)