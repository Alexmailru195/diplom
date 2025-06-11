# orders/serializers.py

from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Сериализатор для позиций заказа
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    """
    Полный сериализатор заказа
    """
    order_items = OrderItemSerializer(many=True, read_only=True)

    status_display = serializers.SerializerMethodField()
    delivery_type_display = serializers.SerializerMethodField()
    payment_type_display = serializers.SerializerMethodField()

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_delivery_type_display(self, obj):
        return obj.get_delivery_type_display()

    def get_payment_type_display(self, obj):
        return obj.get_payment_type_display()

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'status',
            'status_display',
            'delivery_type',
            'delivery_type_display',
            'payment_type',
            'payment_type_display',
            'address',
            'total_price',
            'created_at',
            'order_items'
        ]
        read_only_fields = ['id', 'user', 'total_price', 'created_at']


class CreateOrderSerializer(serializers.Serializer):
    """
    Сериализатор для создания заказа через API
    """
    delivery_type = serializers.ChoiceField(choices=Order.DELIVERY_CHOICES)
    payment_type = serializers.ChoiceField(choices=Order.PAYMENT_CHOICES)
    address = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        """
        Этот метод нужен, чтобы Serializer мог работать с .save()
        Реальная логика оформления заказа находится в ViewSet или utils.py
        """
        # Реальную реализацию делаем в ViewSet
        return validated_data

    def update(self, instance, validated_data):
        raise NotImplementedError("Метод обновления не реализован")
