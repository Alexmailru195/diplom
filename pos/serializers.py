from rest_framework import serializers
from .models import PointOfSale


class PointOfSaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointOfSale
        fields = ['id', 'name', 'address', 'working_hours', 'contact_phone', 'is_active']
