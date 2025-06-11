from rest_framework import serializers
from .models import Warehouse, Inventory


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ['id', 'name', 'address', 'is_active']


class InventorySerializer(serializers.ModelSerializer):
    warehouse = WarehouseSerializer(read_only=True)
    warehouse_id = serializers.PrimaryKeyRelatedField(
        queryset=Warehouse.objects.all(),
        source='warehouse',
        write_only=True
    )

    class Meta:
        model = Inventory
        fields = ['id', 'warehouse', 'warehouse_id', 'product', 'stock', 'reserved', 'updated_at']
        read_only_fields = ['updated_at']
