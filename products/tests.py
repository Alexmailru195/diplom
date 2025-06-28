from django.test import TestCase
from django.urls import reverse
from products.models import Product, Category


class ProductListViewTest(TestCase):
    def test_product_list_view_all_products(self):
        response = self.client.get(reverse('products:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('products', response.context)

    def test_product_list_view_with_category_filter(self):
        category = Category.objects.create(name='TestCategory')
        Product.objects.create(name='Product1', price=100, category=category)
        url = f"{reverse('products:product_list')}?category={category.id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('selected_category', response.context)

    def test_product_list_view_with_search_query(self):
        Product.objects.create(name='SearchableProduct', price=150)
        url = f"{reverse('products:product_list')}?q=Searchable"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.context['products'].object_list) >= 1)

    def test_product_list_view_sorting_by_price_asc(self):
        Product.objects.create(name='ProductA', price=300)
        Product.objects.create(name='ProductB', price=200)
        Product.objects.create(name='ProductC', price=100)
        url = f"{reverse('products:product_list')}?sort=price_asc"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        products = response.context['products'].object_list

        self.assertLessEqual(products[0].price, products[1].price)

    def test_product_list_view_sorting_by_price_desc(self):
        Product.objects.create(name='ProductA', price=300)
        Product.objects.create(name='ProductB', price=200)
        Product.objects.create(name='ProductC', price=100)
        url = f"{reverse('products:product_list')}?sort=price_desc"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        products = response.context['products'].object_list

        # Debug-вывод
        print("Список товаров:", [p.name for p in products])
        print("Цены:", [str(p.price) for p in products])

        self.assertGreaterEqual(products[0].price, products[1].price)