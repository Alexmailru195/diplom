# products/views.py

from django.shortcuts import render, get_object_or_404, redirect

from inventory.models import PointInventory
from . import models
from .models import Product, Category, ProductImage
from django.db.models import Count
from .forms import CategoryForm, ProductForm, ProductImageForm
from django.db.models import Sum


def product_list_view(request):
    category_id = request.GET.get('category')
    selected_category = None
    products = []

    if category_id and category_id.isdigit():
        selected_category = Category.objects.filter(id=int(category_id)).first()
        if selected_category:
            products = Product.objects.filter(category=selected_category)

    categories = Category.objects.all()

    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
    })


def product_detail_view(request, pk):
    """
    Детали товара: описание, атрибуты, изображения
    """
    product = get_object_or_404(Product, pk=pk, is_active=True)
    attributes = product.attributes.all()
    inventories = PointInventory.objects.filter(product=product).select_related('point')
    images = product.images.all()

    context = {
        'product': product,
        'inventories': inventories,
        'attributes': attributes,
        'images': images
    }

    # Получаем общее количество на всех точках
    total_stock = PointInventory.objects.filter(product=product).aggregate(total=Sum('quantity'))['total'] or 0

    return render(request, 'products/product_detail.html', {
        'product': product,
        'images': images,
        'attributes': attributes,
        'total_stock': total_stock
    })

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


def create_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('products:category_list')
    else:
        form = CategoryForm()

    return render(request, 'products/create_category.html', {'form': form})


def create_product(request):
    product_form = ProductForm()
    image_form = ProductImageForm()

    if request.method == 'POST':
        product_form = ProductForm(request.POST)
        image_form = ProductImageForm(request.POST, request.FILES)

        if product_form.is_valid():
            product = product_form.save()

            # Сохраняем изображение
            if image_form.is_valid() and 'image' in request.FILES:
                ProductImage.objects.create(
                    product=product,
                    image=request.FILES['image'],
                    is_main=True
                )

            return redirect('products:product_list')

    return render(request, 'products/create_product.html', {
        'product_form': product_form,
        'image_form': image_form
    })


def category_list_view(request):
    categories = Category.objects.all()
    return render(request, 'products/category_list.html', {'categories': categories})


def category_detail_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    return render(request, 'products/product_list.html', {
        'products': products,
        'category': category
    })
