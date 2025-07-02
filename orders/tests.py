from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from orders.models import Order
from cart.models import Cart, CartItem
from products.models import Product


User = get_user_model()


class OrderConfirmViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.product = Product.objects.create(name='Ручка', price=100)

        # Создаём точку самовывоза и склад для успешного прохождения логики списания
        from pos.models import Point
        self.pickup_point = Point.objects.create(name="Пункт самовывоза")
        self.warehouse = Point.objects.create(name="Склад", is_warehouse=True)

        # Добавляем товар на склад
        from inventory.models import PointInventory
        PointInventory.objects.create(point=self.warehouse, product=self.product, quantity=10)

    def test_order_confirm_view_get(self):
        # Создаём товар в корзине
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=1)

        # Авторизуем пользователя
        self.assertTrue(self.client.login(username='testuser', password='password'))

        # Выполняем GET-запрос
        response = self.client.get(reverse('orders:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_order_confirm_view_post_success(self):
        # Создаем корзину и товар в ней
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=1)

        data = {
            'delivery_type': 'courier',
            'address': 'Ленинский проспект, 800',
            'delivery_date': '2025-06-29',
            'time_slot': 'afternoon',
            'name': 'Иван Иванов',
            'phone': '+79991234567',
            'email': 'ivan@example.com',
            'payment_type': 'online'
        }

        self.assertTrue(self.client.login(username='testuser', password='password'))
        response = self.client.post(reverse('orders:checkout'), data=data)

        # Проверяем статус ответа
        self.assertEqual(response.status_code, 302)

        # Получаем ID заказа после создания
        order = Order.objects.filter(user=self.user).first()
        self.assertIsNotNone(order)  # Проверяем, что заказ существует

        # Проверяем URL редиректа
        self.assertTrue(response.url.startswith(reverse('orders:order_detail', args=[order.id])))

        # Проверяем поля заказа
        self.assertEqual(order.name, 'Иван Иванов')
        self.assertEqual(order.phone, '+79991234567')
        self.assertEqual(order.email, 'ivan@example.com')
        self.assertEqual(order.delivery_type, 'courier')
        self.assertEqual(order.payment_type, 'online')

        # Проверяем, что корзина очищена
        cart_items = CartItem.objects.filter(cart__user=self.user)
        self.assertEqual(cart_items.count(), 0)
