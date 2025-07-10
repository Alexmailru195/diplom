# products/views.py
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404, redirect

from inventory.models import PointInventory
from .forms import CategoryForm, ProductForm, ProductImageForm
from .models import Product, Category, ProductImage


def product_list_view(request):
    """
    Отображает список всех товаров.
    Позволяет фильтровать товары по категории и поисковому запросу,
    а также сортировать их по цене или названию.
    """

    query = request.GET.get('q', '')
    category_id = request.GET.get('category')
    sort_by = request.GET.get('sort', 'default')

    # Получаем все категории
    categories = Category.objects.all()

    # Фильтруем товары
    if query:
        products = Product.objects.filter(name__icontains=query)
        selected_category = None
    elif category_id:
        selected_category = get_object_or_404(Category, id=category_id)
        products = selected_category.products.all()
    else:
        products = Product.objects.all()
        selected_category = None

    # Сортировка
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'name_asc':
        products = products.order_by('name')
    elif sort_by == 'name_desc':
        products = products.order_by('-name')

    # Пагинация
    paginator = Paginator(products, 8)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.page(1)

    return render(request, 'products/product_list.html', {
        'products': page_obj,
        'categories': categories,
        'query': query,
        'sort_by': sort_by,
        'selected_category': selected_category
    })


def product_detail_view(request, pk):
    """
    Отображает детали конкретного товара.
    Включает описание, атрибуты, изображения и информацию об остатках на складах.

    Args:
        pk (int): ID товара.

    Returns:
        HttpResponse: Отрендеренная страница с информацией о товаре.
    """
    product = get_object_or_404(Product, pk=pk, is_active=True)
    attributes = product.attributes.all()
    inventories = PointInventory.objects.filter(product=product).select_related('point')
    images = product.images.all()

    total_stock = PointInventory.objects.filter(product=product).aggregate(total=Sum('quantity'))['total'] or 0

    return render(request, 'products/product_detail.html', {
        'product': product,
        'inventories': inventories,
        'attributes': attributes,
        'images': images,
        'total_stock': total_stock
    })


def category_product_list_view(request, category_pk):
    """
    Отображает список товаров в определённой категории.

    Args:
        category_pk (int): ID категории.

    Returns:
        HttpResponse: Отрендеренная страница с товарами категории.
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
    """
    Представление для создания новой категории.
    Использует форму CategoryForm и отправляет уведомления при успешном сохранении.
    """
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Категория успешно создана!")
            return redirect('products:create_category')
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = CategoryForm()

    return render(request, 'products/create_category.html', {'form': form})


def create_product(request):
    """
    Представление для создания нового товара.
    Позволяет заполнить данные о товаре и загрузить главное изображение.
    """
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
    """
    Отображает список всех категорий.
    """
    categories = Category.objects.all()
    return render(request, 'products/category_list.html', {'categories': categories})


def category_detail_view(request, category_id):
    """
    Отображает товары в выбранной категории.

    Args:
        category_id (int): ID категории.

    Returns:
        HttpResponse: Отрендеренная страница с товарами категории.
    """
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    return render(request, 'products/product_list.html', {
        'products': products,
        'category': category
    })


def search_view(request):
    """
    Поиск товаров по имени.
    Возвращает результаты поиска и отображает их на странице списка товаров.
    """
    query = request.GET.get('q', '')
    products = []

    if query:
        products = Product.objects.filter(name__icontains=query)

    return render(request, 'products/product_list.html', {
        'products': products,
        'query': query
    })
