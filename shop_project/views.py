# shop_project/views.py

from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from products.models import Product
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages


def home_view(request):
    """
    Главная страница с популярными товарами
    """
    popular_products = Product.objects.filter(is_active=True).order_by('-id')[:3]

    return render(request, 'home.html', {
        'popular_products': popular_products
    })


def about_view(request):
    """
    Страница "О магазине"
    """
    return render(request, 'about.html')


def contact_view(request):
    """
    Страница "Контакты"
    """
    return render(request, 'contact.html')


def page_not_found_view(request, exception=None):
    """
    Кастомная страница 404
    """
    return render(request, '404.html', status=404)


def server_error_view(request):
    """
    Кастомная страница 500
    """
    return render(request, '500.html', status=500)

def logout_view(request):
    logout(request)
    messages.info(request, "Вы вышли из аккаунта")
    return redirect('home')