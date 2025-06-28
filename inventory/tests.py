from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import PointInventory, Product, Point, StockHistory, StockMovement


class InventoryTestBase(TestCase):
    def setUp(self):
        self.client = Client()
        User = get_user_model()
        self.user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='password'
        )
        self.product1 = Product.objects.create(name='Ручка', price=100)
        self.product2 = Product.objects.create(name='Блокнот', price=500)
        self.point1 = Point.objects.create(name='Пункт выдачи 1')
        self.point2 = Point.objects.create(name='Пункт выдачи 2')

        # Начальные данные
        self.inventory1 = PointInventory.objects.create(product=self.product1, point=self.point1, quantity=50)
        self.inventory2 = PointInventory.objects.create(product=self.product2, point=self.point2, quantity=3)


class AddInventoryViewTest(InventoryTestBase):
    def test_add_inventory_view_post(self):
        data = {
            'product': self.product1.id,
            'point': self.point1.id,
            'quantity': 10
        }

        self.client.force_login(self.user)
        response = self.client.post(reverse('inventory:add'), data=data)

        self.assertEqual(response.status_code, 302)
        inv = PointInventory.objects.get(product=self.product1, point=self.point1)
        self.assertEqual(inv.quantity, 60)  # 50 + 10

    def test_add_inventory_create_new(self):
        new_product = Product.objects.create(name='Новый товар', price=200)
        new_point = Point.objects.create(name='Новая точка')

        data = {
            'product': new_product.id,
            'point': new_point.id,
            'quantity': 20
        }

        self.client.force_login(self.user)
        response = self.client.post(reverse('inventory:add'), data=data)

        self.assertEqual(response.status_code, 302)
        inv = PointInventory.objects.get(product=new_product, point=new_point)
        self.assertEqual(inv.quantity, 20)


class MoveInventoryViewTest(InventoryTestBase):
    def test_move_inventory_success(self):
        data = {
            'product': self.product1.id,
            'from_point': self.point1.id,
            'to_point': self.point2.id,
            'quantity': 10
        }

        self.client.force_login(self.user)
        response = self.client.post(reverse('inventory:move_inventory'), data=data)

        from_inv = PointInventory.objects.get(product=self.product1, point=self.point1)
        to_inv = PointInventory.objects.get(product=self.product1, point=self.point2)
        self.assertEqual(from_inv.quantity, 40)
        self.assertEqual(to_inv.quantity, 10)

        movement = StockMovement.objects.filter(movement_type='move').first()
        self.assertIsNotNone(movement)

    def test_move_inventory_insufficient_quantity(self):
        data = {
            'product': self.product2.id,
            'from_point': self.point2.id,
            'to_point': self.point1.id,
            'quantity': 10
        }

        self.client.force_login(self.user)
        response = self.client.post(reverse('inventory:move_inventory'), data=data)

        self.assertEqual(response.status_code, 200)
        from_inv = PointInventory.objects.get(product=self.product2, point=self.point2)
        self.assertEqual(from_inv.quantity, 3)


class InventoryListViewTest(InventoryTestBase):
    def test_inventory_list_filter_by_product(self):
        url = f"{reverse('inventory:stock_list')}?product={self.product1.id}"
        self.client.force_login(self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        inventories = response.context['inventories']
        self.assertEqual(len(inventories), 1)
        self.assertEqual(inventories[0].product, self.product1)

    def test_inventory_list_filter_by_point(self):
        url = f"{reverse('inventory:stock_list')}?point={self.point1.id}"
        self.client.force_login(self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        inventories = response.context['inventories']
        self.assertEqual(len(inventories), 1)
        self.assertEqual(inventories[0].point, self.point1)


class LowStockAlertTest(InventoryTestBase):
    def test_low_stock_alert(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('inventory:low_stock_alert'))

        self.assertEqual(response.status_code, 200)
        inventories = response.context['inventories']
        self.assertEqual(len(inventories), 1)
        self.assertEqual(inventories[0], self.inventory2)


class StockHistoryViewTest(InventoryTestBase):
    def test_stock_history_view(self):
        StockHistory.objects.create(
            product=self.product1,
            point_from=None,
            point_to=self.point1,
            quantity=10,
            action='add',
            comment='Добавлено 10 шт.'
        )

        self.client.force_login(self.user)
        response = self.client.get(reverse('inventory:stock_history'))

        self.assertEqual(response.status_code, 200)
        history = response.context['history']
        self.assertTrue(len(history) >= 1)


class InventoryDetailViewTest(InventoryTestBase):
    def test_inventory_detail_view(self):
        url = reverse('inventory:inventory_detail', args=[self.inventory1.id])
        self.client.force_login(self.user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['inventory'], self.inventory1)
        self.assertEqual(len(response.context['movements']), 0)
