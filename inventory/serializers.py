# inventory/serializers.py

from rest_framework import serializers
from .models import PointInventory, StockMovement
from pos.models import Point
from products.models import Product


class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = ['id', 'name', 'address']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price']


class PointInventorySerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    point = PointSerializer(read_only=True)

    class Meta:
        model = PointInventory
        fields = ['id', 'product', 'point', 'quantity', 'updated_at']


class StockMovementSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMovement
        fields = ['id', 'movement_type', 'from_point', 'to_point', 'quantity', 'description', 'timestamp']