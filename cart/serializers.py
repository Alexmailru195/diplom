# cart/serializers.py

from rest_framework import serializers

from cart.models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отдельной позиции корзины.
    Включает информацию о товаре, его цене и общей стоимости по количеству.
    """

    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(
        source='product.price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    total_price = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'total_price']
        extra_kwargs = {'product': {'required': True}}

    def get_total_price(self, obj):
        """Возвращает общую стоимость одного товара с учётом количества."""
        return obj.product.price * obj.quantity


class CartSerializer(serializers.ModelSerializer):
    """
    Сериализатор для корзины пользователя.
    Отображает список товаров в корзине, а также общее количество и сумму.
    """

    items = CartItemSerializer(many=True, source='items')
    total_items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_items', 'total_price']

    def get_total_items(self, obj):
        """Возвращает общее количество товаров в корзине."""
        return obj.items.count()

    def get_total_price(self, obj):
        """Возвращает общую сумму всех товаров в корзине."""
        return sum(item.total_price for item in obj.items.all())


class AddToCartSerializer(serializers.Serializer):
    """
    Сериализатор для добавления товара в корзину.
    Принимает ID товара и количество (по умолчанию 1).
    """

    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate_product_id(self, value):
        """
        Проверяет, существует ли товар с указанным ID.

        Args:
            value (int): ID товара.

        Raises:
            ValidationError: Если товар не найден.

        Returns:
            int: Валидированный ID товара.
        """
        from products.models import Product
        if not Product.objects.filter(id=value).exists():
            raise serializers.ValidationError("Товар не найден")
        return value
