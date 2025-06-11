from rest_framework import viewsets
from .models import Product
from .serializers import ProductSerializer
from django.shortcuts import render


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


def products_view(request):
    return render(request, 'products/product_list.html')


def product_list(request):
    # Пока просто заглушка
    return render(request, 'products/product_list.html')


def product_detail_view(request, product_id):
    return render(request, 'products/product_detail.html', {'product_id': product_id})
