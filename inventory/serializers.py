# inventory/serializers.py

from rest_framework import serializers

from orders.models import Order
from .models import ProductInventory, StockMovement


class StockMovementSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_inventory.product.name', read_only=True)

    class Meta:
        model = StockMovement
        fields = [
            'id',
            'product_inventory',
            'product_name',
            'movement_type',
            'quantity',
            'timestamp',
            'related_order',
            'description'
        ]
        read_only_fields = ['timestamp']


class ProductInventorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    movements = StockMovementSerializer(many=True, read_only=True)

    class Meta:
        model = ProductInventory
        fields = ['id', 'product', 'product_name', 'quantity', 'updated_at', 'movements']
        read_only_fields = ['id', 'updated_at']


class InventoryAdjustSerializer(serializers.Serializer):
    movement_type = serializers.ChoiceField(
        choices=StockMovement.MOVEMENT_TYPES
    )
    quantity = serializers.IntegerField()
    related_order = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(),
        required=False,
        allow_null=True
    )
    description = serializers.CharField(required=False, allow_blank=True)