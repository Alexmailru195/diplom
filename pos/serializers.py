# pos/serializers.py

from rest_framework import serializers
from .models import SalesPoint, PointInventory, Sale
from products.models import Product
from users.models import User


class PointInventorySerializer(serializers.ModelSerializer):
    """
    Для отображения остатков товара в точке
    """
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(
        source='product.price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = PointInventory
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'updated_at']
        read_only_fields = ['updated_at']


class SalesPointSerializer(serializers.ModelSerializer):
    """
    Полный сериализатор для точки продаж
    """
    inventory = PointInventorySerializer(many=True, read_only=True)

    class Meta:
        model = SalesPoint
        fields = ['id', 'name', 'address', 'manager', 'created_at', 'inventory']
        read_only_fields = ['created_at', 'inventory']


class SaleSerializer(serializers.Serializer):
    """
    Сериализатор для оформления продажи через POS
    """
    sales_point_id = serializers.IntegerField()
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

    def validate_sales_point_id(self, value):
        from .models import SalesPoint
        if not SalesPoint.objects.filter(id=value).exists():
            raise serializers.ValidationError("Точка продаж не найдена")
        return value

    def validate_product_id(self, value):
        from products.models import Product
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("Товар не найден")
        return value

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Количество должно быть больше нуля")
        return value

    def validate(self, data):
        """
        Дополнительная проверка: есть ли нужное количество товара в точке
        """
        try:
            point_inventory = PointInventory.objects.get(
                sales_point_id=data['sales_point_id'],
                product_id=data['product_id']
            )
            if point_inventory.quantity < data['quantity']:
                raise serializers.ValidationError({
                    'quantity': "Недостаточно товара в наличии"
                })
        except PointInventory.DoesNotExist:
            raise serializers.ValidationError({
                'product_id': "Товар не доступен в этой точке"
            })

        return data

    def create(self, validated_data):
        """
        Оформление продажи и обновление инвентаря
        """
        sales_point_id = validated_data['sales_point_id']
        product_id = validated_data['product_id']
        quantity = validated_data['quantity']

        # Обновляем инвентарь
        inventory = PointInventory.objects.get(sales_point_id=sales_point_id, product_id=product_id)
        inventory.quantity -= quantity
        inventory.save()

        # Создаем запись о продаже
        sale = Sale.objects.create(
            sales_point_id=sales_point_id,
            product_id=product_id,
            quantity=quantity,
            user_id=validated_data.get('user_id') or None
        )

        return sale