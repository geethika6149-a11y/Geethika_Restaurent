from django.contrib import admin
from .models import Category, MenuItem, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'slug', 'display_order')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('display_order',)
    search_fields = ('name',)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_vegetarian', 'is_available')
    list_filter = ('category', 'is_vegetarian', 'is_available')
    list_editable = ('price', 'is_available', 'is_vegetarian')
    search_fields = ('name', 'description')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('menu_item', 'price', 'quantity', 'total_price')

    def total_price(self, instance):
        return instance.total_price
    total_price.short_description = "Subtotal"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_code', 'customer_name', 'table_number', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'table_number')
    list_editable = ('status',)
    search_fields = ('order_code', 'customer_name', 'customer_phone', 'table_number')
    readonly_fields = ('order_code', 'created_at', 'updated_at', 'subtotal', 'tax', 'total_amount')
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'menu_item', 'quantity', 'price')
    list_filter = ('order__status', 'menu_item')
    search_fields = ('order__order_code', 'menu_item__name')
