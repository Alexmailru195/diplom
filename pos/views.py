# pos/views.py
from rest_framework.decorators import action
from django.shortcuts import render, get_object_or_404, redirect
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from .models import SalesPoint, PointInventory, Sale
from .serializers import SalesPointSerializer, SaleSerializer


class PosViewSet(ViewSet):
    """
    API endpoint для работы с точками продаж и продажами
    """

    def list(self, request):
        """
        Получить список всех точек продаж
        """
        points = SalesPoint.objects.all()
        serializer = SalesPointSerializer(points, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Получить детали точки продаж
        """
        try:
            point = SalesPoint.objects.get(pk=pk)
            inventories = PointInventory.objects.filter(sales_point=point)
            inventory_serializer = SaleSerializer(inventories, many=True)
            return Response({
                'point': SalesPointSerializer(point).data,
                'inventory': inventory_serializer.data
            })
        except SalesPoint.DoesNotExist:
            return Response({"detail": "Точка не найдена"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def make_sale(self, request):
        """
        Оформить продажу через API
        """
        serializer = SaleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sales_point_id = serializer.validated_data['sales_point_id']
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']

        try:
            point_inventory = PointInventory.objects.get(
                sales_point_id=sales_point_id,
                product_id=product_id
            )
            if point_inventory.quantity < quantity:
                return Response({"detail": "Недостаточно товара в точке"},
                                status=status.HTTP_400_BAD_REQUEST)

            point_inventory.quantity -= quantity
            point_inventory.save()

            sale = Sale.objects.create(
                sales_point_id=sales_point_id,
                product_id=product_id,
                quantity=quantity,
                user=request.user
            )

            return Response({
                "detail": "Продажа оформлена",
                "sale_id": sale.id,
                "total_price": sale.total_price
            }, status=status.HTTP_201_CREATED)

        except PointInventory.DoesNotExist:
            return Response({"detail": "Товар не доступен в этой точке"},
                            status=status.HTTP_400_BAD_REQUEST)


def pos_list_view(request):
    """
    Шаблон: Список всех точек продаж
    """
    points = SalesPoint.objects.all()
    return render(request, 'pos/pos_list.html', {'points': points})


def pos_detail_view(request, pk):
    """
    Шаблон: Детали точки и остатки товаров
    """
    point = get_object_or_404(SalesPoint, pk=pk)
    inventory = PointInventory.objects.filter(sales_point=point)
    return render(request, 'pos/pos_detail.html', {
        'point': point,
        'inventory': inventory
    })


def make_sale_view(request):
    """
    Шаблон: Обработка формы продажи через POST
    """
    if request.method == 'POST':
        sales_point_id = request.POST.get('sales_point_id')
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))

        try:
            inventory = PointInventory.objects.get(
                sales_point_id=sales_point_id,
                product_id=product_id
            )
            if inventory.quantity < quantity:
                return render(request, 'error.html', {"message": "Недостаточно товара"})

            inventory.quantity -= quantity
            inventory.save()

            Sale.objects.create(
                sales_point_id=sales_point_id,
                product_id=product_id,
                quantity=quantity,
                user=request.user
            )

            return redirect('pos_detail', pk=sales_point_id)

        except PointInventory.DoesNotExist:
            return render(request, 'error.html', {"message": "Товар не найден в точке"})