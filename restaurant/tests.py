from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from restaurant.models import Category, MenuItem, Order, OrderItem
import json


class RestaurantFlowTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Appetizers', icon='bi-egg-fried', display_order=1)
        self.item1 = MenuItem.objects.create(
            category=self.category,
            name='Truffle Fries',
            price=Decimal('10.00'),
            is_vegetarian=True,
            is_available=True
        )
        self.item2 = MenuItem.objects.create(
            category=self.category,
            name='Spicy Wings',
            price=Decimal('15.00'),
            is_vegetarian=False,
            is_available=True
        )
        self.item_unavailable = MenuItem.objects.create(
            category=self.category,
            name='Seasonal Special',
            price=Decimal('20.00'),
            is_vegetarian=False,
            is_available=False
        )

    def test_menu_view(self):
        response = self.client.get(reverse('menu'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Truffle Fries')
        self.assertContains(response, 'Spicy Wings')

    def test_category_filtering(self):
        main_cat = Category.objects.create(name='Main Course', icon='bi-fire', display_order=2)
        burger = MenuItem.objects.create(
            category=main_cat,
            name='Gourmet Burger',
            price=Decimal('14.00'),
            is_available=True
        )
        response = self.client.get(reverse('menu') + f'?category={self.category.slug}')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Truffle Fries')
        self.assertNotContains(response, 'Gourmet Burger')

    def test_cart_api_and_session(self):
        # Add item to cart
        payload = json.dumps({'item_id': self.item1.id, 'action': 'add', 'quantity': 2})
        response = self.client.post(reverse('api_update_cart'), data=payload, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['cart_count'], 2)
        self.assertEqual(data['subtotal'], '20.00')
        self.assertEqual(data['tax'], '1.00')  # 5% of 20.00
        self.assertEqual(data['grand_total'], '21.00')

    def test_checkout_and_order_creation(self):
        # Set session cart
        session = self.client.session
        session['cart'] = {str(self.item1.id): 2, str(self.item2.id): 1}
        session.save()

        post_data = {
            'customer_name': 'Jane Doe',
            'customer_phone': '555-1234',
            'customer_email': 'jane@example.com',
            'table_number': 5,
            'special_instructions': 'Extra napkins please'
        }
        response = self.client.post(reverse('checkout'), data=post_data)
        self.assertEqual(response.status_code, 302)

        # Verify order in DB
        order = Order.objects.get(customer_name='Jane Doe')
        self.assertEqual(order.table_number, 5)
        self.assertEqual(order.subtotal, Decimal('35.00'))  # 2 * 10 + 1 * 15
        self.assertEqual(order.tax, Decimal('1.75'))  # 5% of 35.00
        self.assertEqual(order.total_amount, Decimal('36.75'))
        self.assertEqual(order.status, Order.STATUS_RECEIVED)
        self.assertEqual(order.items.count(), 2)

    def test_kitchen_status_progression(self):
        order = Order.objects.create(
            customer_name='Chef Test',
            customer_phone='555-9999',
            table_number=7,
            subtotal=Decimal('10.00'),
            tax=Decimal('0.50'),
            total_amount=Decimal('10.50'),
            status=Order.STATUS_RECEIVED
        )

        # Update to Preparing
        resp = self.client.post(reverse('kitchen_update_status', args=[order.id]), {'status': 'Preparing'})
        self.assertEqual(resp.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, 'Preparing')

        # Update to Ready
        resp = self.client.post(reverse('kitchen_update_status', args=[order.id]), {'status': 'Ready'})
        self.assertEqual(resp.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, 'Ready')

        # Update to Completed
        resp = self.client.post(reverse('kitchen_update_status', args=[order.id]), {'status': 'Completed'})
        self.assertEqual(resp.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, 'Completed')

    def test_order_tracking_view_and_api(self):
        order = Order.objects.create(
            customer_name='Tracker Test',
            customer_phone='555-8888',
            table_number=3,
            subtotal=Decimal('10.00'),
            tax=Decimal('0.50'),
            total_amount=Decimal('10.50'),
            status=Order.STATUS_PREPARING
        )
        # Tracking page
        resp = self.client.get(reverse('order_detail', args=[order.order_code]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, order.order_code)

        # Live status API
        api_resp = self.client.get(reverse('api_order_status', args=[order.order_code]))
        self.assertEqual(api_resp.status_code, 200)
        data = api_resp.json()
        self.assertEqual(data['status'], 'Preparing')
        self.assertEqual(data['progress_percentage'], 50)
