# inventory/views.py
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from .models import ProductInventory, StockMovement
from .serializers import (
    ProductInventorySerializer,
    InventoryAdjustSerializer,
    StockMovementSerializer
)


class InventoryViewSet(ViewSet):
    """
    API endpoint для управления остатками товаров и их движениями.
    """

    def list(self, request):
        """
        Получить список всех товаров с текущими остатками
        """
        inventories = ProductInventory.objects.all()
        serializer = ProductInventorySerializer(inventories, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Получить детали инвентаря по ID
        """
        try:
            inventory = ProductInventory.objects.get(pk=pk)
            serializer = ProductInventorySerializer(inventory)
            return Response(serializer.data)
        except ProductInventory.DoesNotExist:
            return Response({"detail": "Инвентарь не найден"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def adjust_stock(self, request, pk=None):
        """
        Добавить/уменьшить количество товара (движение остатков)
        Пример POST:
        {
          "movement_type": "in",
          "quantity": 50,
          "description": "Новая поставка"
        }
        """
        try:
            inventory = ProductInventory.objects.get(pk=pk)
        except ProductInventory.DoesNotExist:
            return Response({"detail": "Инвентарь не найден"}, status=status.HTTP_404_NOT_FOUND)

        serializer = InventoryAdjustSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        movement_type = serializer.validated_data['movement_type']
        quantity = serializer.validated_data['quantity']

        # Обновляем количество товара
        if movement_type == 'in':
            inventory.quantity += quantity
        elif movement_type == 'out':
            if inventory.quantity < quantity:
                return Response(
                    {"detail": "Недостаточно товара на складе"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            inventory.quantity -= quantity
        elif movement_type == 'adjust':
            inventory.quantity += quantity

        inventory.save()

        # Создаем запись о движении
        movement = StockMovement.objects.create(
            product_inventory=inventory,
            movement_type=movement_type,
            quantity=quantity,
            related_order=serializer.validated_data.get('related_order'),
            description=serializer.validated_data.get('description')
        )

        movement_serializer = StockMovementSerializer(movement)

        return Response({
            "inventory": ProductInventorySerializer(inventory).data,
            "movement": movement_serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def low_stock_alert(self, request):
        """
        Список товаров с низким остатком (например, меньше 5 шт.)
        """
        threshold = int(request.query_params.get('threshold', 5))
        inventories = ProductInventory.objects.filter(quantity__lt=threshold)
        serializer = ProductInventorySerializer(inventories, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def history(self, request):
        """
        Получить историю движений товаров
        """
        movements = StockMovement.objects.all().order_by('-timestamp')
        page = self.paginate_queryset(movements)
        if page is not None:
            serializer = StockMovementSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = StockMovementSerializer(movements, many=True)
        return Response(serializer.data)