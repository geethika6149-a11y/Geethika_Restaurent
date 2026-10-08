from django.core.management.base import BaseCommand
from restaurant.models import Category, MenuItem, Order, OrderItem
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populates the restaurant database with categories, menu items, and sample orders'

    def handle(self, *args, **options):
        self.stdout.write('Loading sample restaurant data...')

        # Categories
        cat_data = [
            {'name': 'Appetizers', 'icon': 'bi-egg-fried', 'order': 1},
            {'name': 'Main Course', 'icon': 'bi-fire', 'order': 2},
            {'name': 'Desserts', 'icon': 'bi-cake2', 'order': 3},
            {'name': 'Beverages', 'icon': 'bi-cup-hot', 'order': 4},
        ]

        categories = {}
        for c in cat_data:
            cat_obj, created = Category.objects.get_or_create(
                name=c['name'],
                defaults={'icon': c['icon'], 'display_order': c['order']}
            )
            categories[c['name']] = cat_obj
            self.stdout.write(f"Category '{cat_obj.name}' ready.")

        # Menu Items
        items_data = [
            # Appetizers
            {
                'category': 'Appetizers',
                'name': 'Crispy Truffle Fries',
                'description': 'Hand-cut golden fries tossed in aromatic white truffle oil, grated parmesan, and fresh parsley.',
                'price': Decimal('7.99'),
                'is_vegetarian': True,
                'is_available': True,
                'image_url': 'https://images.unsplash.com/photo-1573080496219-bb080dd4f877?auto=format&fit=crop&w=600&q=80',
            },
            {
                'category': 'Appetizers',
                'name': 'Spicy Buffalo Wings',
                'description': 'Crispy fried chicken wings tossed in our signature tangy hot buffalo sauce, served with cool blue cheese dip.',
                'price': Decimal('10.99'),
                'is_vegetarian': False,
                'is_available': True,
                'image_url': 'https://images.unsplash.com/photo-1527477378378-47702f23bfa4?auto=format&fit=crop&w=600&q=80',
            },
            {
                'category': 'Appetizers',
                'name': 'Garlic Butter Bruschetta',
                'description': 'Toasted artisanal sourdough rubbed with roasted garlic, topped with heirloom tomatoes, basil, and balsamic reduction.',
                'price': Decimal('6.49'),
                'is_vegetarian': True,
                'is_available': True,
                'image_url': 'https://images.unsplash.com/photo-1572695157366-5e585ab2b69f?auto=format&fit=crop&w=600&q=80',
            },
            {
                'category': 'Appetizers',
                'name': 'Crispy Calamari',
                'description': 'Golden tempura-fried squid rings served with spicy marinara sauce and charred lemon wedge.',
                'price': Decimal('11.50'),
                'is_vegetarian': False,
                'is_available': True,
                'image_url': 'https://images.unsplash.com/photo-1599488615731-7e5c2823ff28?auto=format&fit=crop&w=600&q=80',
            },

            # Main Course
            {
                'category': 'Main Course',
                'name': 'Gourmet Wagyu Burger',
                'description': 'Prime ground wagyu patty, melted aged cheddar, caramelized onions, crisp lettuce, brioche bun, and side fries.',
                'price': Decimal('14.99'),
                'is_vegetarian': False,
                'is_available': True,
                'image_url': 'https://images.unsplash.com/photo-1568901346375-23c9450c58cd?auto=format&fit=crop&w=600&q=80',
            },
            {
                'category': 'Main Course',
                'name': 'Wild Mushroom Risotto',
                'description': 'Arborio rice slowly simmered with porcini and cremini mushrooms, white wine, truffle butter, and pecorino romano.',
                'price': Decimal('15.50'),
                'is_vegetarian': True,
                'is_available': True,
                'image_url': 'https://images.unsplash.com/photo-1633964913295-ceb43826e7c9?auto=format&fit=crop&w=600&q=80',
            },
            {
                'category': 'Main Course',
                'name': 'Grilled Atlantic Salmon',
                'description': 'Pan-seared Atlantic salmon fillet with lemon herb butter glaze, garlic mashed potatoes, and sautéed asparagus.',
                'price': Decimal('18.99'),
                'is_vegetarian': False,
                'is_available': True,
                'image_url': 'https://images.unsplash.com/photo-1467003909585-2f8a72700288?auto=format&fit=crop&w=600&q=80',
            },
            {
                'category': 'Main Course',
                'name': 'Margherita Artisan Pizza',
                'description': 'Wood-fired sourdough crust with San Marzano tomato sauce, fresh buffalo mozzarella, virgin olive oil, and fresh basil.',
                'price': Decimal('12.50'),
                'is_vegetarian': True,
                'is_available': True,
                'image_url': 'https://images.unsplash.com/photo-1604382355076-af4b0eb60143?auto=format&fit=crop&w=600&q=80',
            },
            {
                'category': 'Main Course',
                'name': 'Butter Chicken Bowl',
                'description': 'Tender tandoori chicken cooked in velvety tomato, butter, and fenugreek gravy, served with basmati rice and garlic naan.',
                'price': Decimal('15.99'),
                'is_vegetarian': False,
                'is_available': True,
                'image_url': 'https://images.unsplash.com/photo-1603894584373-5ac82b2ae398?auto=format&fit=crop&w=600&q=80',
            },
            {
                'category': 'Main Course',
                'name': 'Garden Veggie Fettuccine',
                'description': 'Fresh fettuccine tossed with zucchini ribbons, cherry tomatoes, baby spinach, roasted garlic oil, and parmesan.',
                'price': Decimal('13.25'),
                'is_vegetarian': True,
                'is_available': True,
                'image_url': 'https://images.unsplash.com/photo-1621996346565-e3d5d62817d4?auto=format&fit=crop&w=600&q=80',
            },

            # Desserts
            {
                'category': 'Desserts',
                'name': 'Molten Chocolate Lava Cake',
                'description': 'Warm dark chocolate cake with a molten fudge center, dusted with powdered sugar and paired with Madagascar vanilla bean gelato.',
                'price': Decimal('7.50'),
                'is_vegetarian': True,
                'is_available': True,
                'image_url': 'https://images.unsplash.com/photo-1606313564200-e75d5e30476c?auto=format&fit=crop&w=600&q=80',
            },
            {
                'category': 'Desserts',
                'name': 'New York Style Cheesecake',
                'description': 'Rich and velvety baked cheesecake on a golden graham cracker crust, drizzled with wild strawberry coulis.',
                'price': Decimal('6.99'),
                'is_vegetarian': True,
                'is_available': True,
                'image_url': 'https://images.unsplash.com/photo-1524351199678-941a58a3df50?auto=format&fit=crop&w=600&q=80',
            },
            {
                'category': 'Desserts',
                'name': 'Tiramisu Classico',
                'description': 'Espresso-soaked ladyfingers layered with whipped mascarpone cream and dusted with bitter cocoa powder.',
                'price': Decimal('7.25'),
                'is_vegetarian': True,
                'is_available': True,
                'image_url': 'https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?auto=format&fit=crop&w=600&q=80',
            },

            # Beverages
            {
                'category': 'Beverages',
                'name': 'Iced Caramel Macchiato',
                'description': 'Freshly pulled espresso layered over chilled whole milk and vanilla syrup, topped with rich buttery caramel drizzle.',
                'price': Decimal('4.75'),
                'is_vegetarian': True,
                'is_available': True,
                'image_url': 'https://images.unsplash.com/photo-1517701550927-30cf4ba1dba5?auto=format&fit=crop&w=600&q=80',
            },
            {
                'category': 'Beverages',
                'name': 'Fresh Mint Lime Mojito',
                'description': 'Crushed organic mint leaves, zesty lime wedges, simple cane syrup, and sparkling soda served over crushed ice.',
                'price': Decimal('5.25'),
                'is_vegetarian': True,
                'is_available': True,
                'image_url': 'https://images.unsplash.com/photo-1551024709-8f23befc6f87?auto=format&fit=crop&w=600&q=80',
            },
            {
                'category': 'Beverages',
                'name': 'Sparkling Berry Lemonade',
                'description': 'Fresh squeezed Meyer lemon juice infused with blackberry and raspberry puree, finished with bubbly club soda.',
                'price': Decimal('4.25'),
                'is_vegetarian': True,
                'is_available': True,
                'image_url': 'https://images.unsplash.com/photo-1513558161293-cdaf765ed2fd?auto=format&fit=crop&w=600&q=80',
            },
        ]

        created_items = {}
        for item in items_data:
            cat = categories[item['category']]
            menu_obj, created = MenuItem.objects.update_or_create(
                category=cat,
                name=item['name'],
                defaults={
                    'description': item['description'],
                    'price': item['price'],
                    'is_vegetarian': item['is_vegetarian'],
                    'is_available': item['is_available'],
                    'image_url': item['image_url'],
                }
            )
            created_items[item['name']] = menu_obj
            self.stdout.write(f"Menu item '{menu_obj.name}' ready.")

        # Sample Orders if none exist
        if Order.objects.count() == 0:
            sample_orders = [
                {
                    'name': 'Alex Johnson',
                    'phone': '555-0142',
                    'table': 4,
                    'status': Order.STATUS_RECEIVED,
                    'notes': 'Extra napkins and dressing on the side.',
                    'items': [('Crispy Truffle Fries', 2), ('Gourmet Wagyu Burger', 1), ('Fresh Mint Lime Mojito', 2)],
                },
                {
                    'name': 'Samantha Lee',
                    'phone': '555-0198',
                    'table': 12,
                    'status': Order.STATUS_PREPARING,
                    'notes': 'Table celebrating an anniversary.',
                    'items': [('Margherita Artisan Pizza', 1), ('Wild Mushroom Risotto', 1), ('Sparkling Berry Lemonade', 2)],
                },
                {
                    'name': 'Marcus Vance',
                    'phone': '555-0233',
                    'table': 8,
                    'status': Order.STATUS_READY,
                    'notes': 'Please pack bill with order.',
                    'items': [('Grilled Atlantic Salmon', 1), ('Molten Chocolate Lava Cake', 1), ('Iced Caramel Macchiato', 1)],
                },
                {
                    'name': 'Emily Davis',
                    'phone': '555-0311',
                    'table': 2,
                    'status': Order.STATUS_COMPLETED,
                    'notes': 'Thank you! Food was amazing.',
                    'items': [('Spicy Buffalo Wings', 1), ('New York Style Cheesecake', 1)],
                },
            ]

            for ord_info in sample_orders:
                subtotal = Decimal('0.00')
                for item_name, qty in ord_info['items']:
                    subtotal += created_items[item_name].price * qty
                tax = (subtotal * Decimal('0.05')).quantize(Decimal('0.01'))
                total = subtotal + tax

                order = Order.objects.create(
                    customer_name=ord_info['name'],
                    customer_phone=ord_info['phone'],
                    table_number=ord_info['table'],
                    special_instructions=ord_info['notes'],
                    status=ord_info['status'],
                    subtotal=subtotal,
                    tax=tax,
                    total_amount=total
                )

                for item_name, qty in ord_info['items']:
                    item_obj = created_items[item_name]
                    OrderItem.objects.create(
                        order=order,
                        menu_item=item_obj,
                        quantity=qty,
                        price=item_obj.price
                    )
                self.stdout.write(f"Sample Order #{order.id} ({order.order_code}) created with status {order.status}.")

        self.stdout.write(self.style.SUCCESS('Successfully populated database with realistic sample data!'))
