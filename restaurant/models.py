from django.db import models
from django.utils.text import slugify
import uuid


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(
        max_length=50, 
        blank=True, 
        default='bi-egg-fried', 
        help_text='Bootstrap icon class name, e.g., bi-cup-hot, bi-egg-fried, bi-cake2'
    )
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['display_order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_vegetarian = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    image_url = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} (${self.price})"


class Order(models.Model):
    STATUS_RECEIVED = 'Received'
    STATUS_PREPARING = 'Preparing'
    STATUS_READY = 'Ready'
    STATUS_COMPLETED = 'Completed'

    STATUS_CHOICES = [
        (STATUS_RECEIVED, 'Received'),
        (STATUS_PREPARING, 'Preparing'),
        (STATUS_READY, 'Ready'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    order_code = models.CharField(max_length=20, unique=True, blank=True, editable=False)
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    customer_email = models.EmailField(blank=True)
    table_number = models.PositiveIntegerField(help_text='Dining table number (e.g. 1 - 50)')
    special_instructions = models.TextField(blank=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_RECEIVED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_code:
            # Generate a readable short code like ORD-48291
            self.order_code = f"ORD-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.id} ({self.order_code}) - Table {self.table_number} [{self.status}]"

    @property
    def progress_percentage(self):
        mapping = {
            self.STATUS_RECEIVED: 25,
            self.STATUS_PREPARING: 50,
            self.STATUS_READY: 75,
            self.STATUS_COMPLETED: 100,
        }
        return mapping.get(self.status, 25)

    @property
    def badge_color(self):
        mapping = {
            self.STATUS_RECEIVED: 'warning',
            self.STATUS_PREPARING: 'info',
            self.STATUS_READY: 'primary',
            self.STATUS_COMPLETED: 'success',
        }
        return mapping.get(self.status, 'secondary')


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2, help_text='Price at the time of ordering')

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name} for Order #{self.order.id}"

    @property
    def total_price(self):
        return self.quantity * self.price
