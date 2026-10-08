from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST, require_http_methods
from django.db import transaction
from django.contrib import messages
from decimal import Decimal
import json

from .models import Category, MenuItem, Order, OrderItem
from .forms import CheckoutForm, OrderLookupForm, OrderStatusUpdateForm


TAX_RATE = Decimal('0.05')  # 5% tax rate


def _get_cart(session):
    """Helper to retrieve and format cart items from session with verified DB data."""
    raw_cart = session.get('cart', {})
    cart_items = []
    subtotal = Decimal('0.00')

    # Fetch menu items present in cart
    item_ids = [int(k) for k in raw_cart.keys() if str(k).isdigit()]
    items_by_id = {item.id: item for item in MenuItem.objects.filter(id__in=item_ids)}

    for item_id_str, qty in list(raw_cart.items()):
        try:
            item_id = int(item_id_str)
            qty = int(qty)
            if qty <= 0:
                continue
            if item_id in items_by_id:
                menu_item = items_by_id[item_id]
                line_total = menu_item.price * qty
                subtotal += line_total
                cart_items.append({
                    'menu_item': menu_item,
                    'quantity': qty,
                    'line_total': line_total,
                })
        except (ValueError, TypeError):
            continue

    tax = (subtotal * TAX_RATE).quantize(Decimal('0.01'))
    grand_total = subtotal + tax

    return {
        'items': cart_items,
        'subtotal': subtotal,
        'tax': tax,
        'grand_total': grand_total,
        'total_count': sum(item['quantity'] for item in cart_items),
    }


def menu_view(request):
    """Customer-facing food menu with category filter and search."""
    categories = Category.objects.prefetch_related('items').all()
    selected_category_slug = request.GET.get('category', '').strip()
    search_query = request.GET.get('q', '').strip()

    items = MenuItem.objects.select_related('category').all()

    if selected_category_slug and selected_category_slug != 'all':
        items = items.filter(category__slug=selected_category_slug)

    if search_query:
        items = items.filter(name__icontains=search_query) | items.filter(description__icontains=search_query)

    cart_summary = _get_cart(request.session)

    context = {
        'categories': categories,
        'menu_items': items,
        'selected_category': selected_category_slug,
        'search_query': search_query,
        'cart_summary': cart_summary,
    }
    return render(request, 'restaurant/menu.html', context)


def cart_view(request):
    """Shopping cart page with subtotal, tax, and grand total."""
    cart_summary = _get_cart(request.session)
    checkout_form = CheckoutForm()

    context = {
        'cart': cart_summary,
        'form': checkout_form,
    }
    return render(request, 'restaurant/cart.html', context)


@require_POST
def api_update_cart(request):
    """AJAX endpoint to update item quantity or add item to cart session."""
    try:
        data = json.loads(request.body.decode('utf-8'))
        item_id = str(data.get('item_id'))
        action = data.get('action', 'add')  # 'add', 'set', 'remove'
        quantity = int(data.get('quantity', 1))

        # Check item exists
        menu_item = get_object_or_404(MenuItem, id=int(item_id))
        if not menu_item.is_available:
            return JsonResponse({'success': False, 'error': f"{menu_item.name} is currently unavailable."}, status=400)

        cart = request.session.get('cart', {})

        if action == 'add':
            cart[item_id] = cart.get(item_id, 0) + quantity
        elif action == 'set':
            if quantity > 0:
                cart[item_id] = quantity
            else:
                cart.pop(item_id, None)
        elif action == 'remove':
            cart.pop(item_id, None)

        request.session['cart'] = cart
        request.session.modified = True

        summary = _get_cart(request.session)
        return JsonResponse({
            'success': True,
            'cart_count': summary['total_count'],
            'subtotal': str(summary['subtotal']),
            'tax': str(summary['tax']),
            'grand_total': str(summary['grand_total']),
            'item_qty': cart.get(item_id, 0),
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_POST
def api_sync_local_storage(request):
    """Sync localStorage cart to server session."""
    try:
        data = json.loads(request.body.decode('utf-8'))
        incoming_cart = data.get('cart', {})
        cleaned_cart = {}

        for item_id_str, qty in incoming_cart.items():
            if str(item_id_str).isdigit() and int(qty) > 0:
                # verify availability
                if MenuItem.objects.filter(id=int(item_id_str), is_available=True).exists():
                    cleaned_cart[str(item_id_str)] = int(qty)

        request.session['cart'] = cleaned_cart
        request.session.modified = True

        summary = _get_cart(request.session)
        return JsonResponse({
            'success': True,
            'cart_count': summary['total_count'],
            'subtotal': str(summary['subtotal']),
            'tax': str(summary['tax']),
            'grand_total': str(summary['grand_total']),
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def checkout_view(request):
    """Process checkout, validate server-side totals, and create order."""
    cart_summary = _get_cart(request.session)

    if not cart_summary['items']:
        messages.warning(request, "Your cart is empty. Please add items to order.")
        return redirect('menu')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                order = form.save(commit=False)

                # Re-verify items and calculate server-side totals
                subtotal = Decimal('0.00')
                order_items_to_create = []

                for item in cart_summary['items']:
                    menu_item = item['menu_item']
                    # Double check item is still available
                    if not menu_item.is_available:
                        messages.error(request, f"Item '{menu_item.name}' is out of stock. Please remove it from your cart.")
                        return redirect('cart')

                    qty = item['quantity']
                    line_price = menu_item.price * qty
                    subtotal += line_price

                    order_items_to_create.append(OrderItem(
                        order=order,
                        menu_item=menu_item,
                        quantity=qty,
                        price=menu_item.price
                    ))

                tax = (subtotal * TAX_RATE).quantize(Decimal('0.01'))
                grand_total = subtotal + tax

                order.subtotal = subtotal
                order.tax = tax
                order.total_amount = grand_total
                order.status = Order.STATUS_RECEIVED
                order.save()

                # Bulk create order items
                for oi in order_items_to_create:
                    oi.order = order
                    oi.save()

                # Clear Django session cart
                request.session['cart'] = {}
                request.session.modified = True

                messages.success(request, f"Order #{order.id} ({order.order_code}) placed successfully! The kitchen has received your ticket.")
                return redirect('order_detail', order_identifier=order.order_code)
    else:
        form = CheckoutForm()

    context = {
        'form': form,
        'cart': cart_summary,
    }
    return render(request, 'restaurant/checkout.html', context)


def order_lookup_view(request):
    """Lookup page for tracking orders by ID or Order Code."""
    query = request.GET.get('order_id', '').strip()
    if query:
        return redirect('order_detail', order_identifier=query)

    form = OrderLookupForm()
    if request.method == 'POST':
        form = OrderLookupForm(request.POST)
        if form.is_valid():
            ident = form.cleaned_data['order_identifier'].strip()
            return redirect('order_detail', order_identifier=ident)

    recent_orders = Order.objects.order_by('-created_at')[:5]
    return render(request, 'restaurant/order_lookup.html', {'form': form, 'recent_orders': recent_orders})


def order_detail_view(request, order_identifier):
    """Live order status tracking page with stepper progress bar."""
    order = None
    if order_identifier.isdigit():
        order = Order.objects.filter(id=int(order_identifier)).first()
    if not order:
        order = Order.objects.filter(order_code__iexact=order_identifier).first()

    if not order:
        messages.error(request, f"No order found with ID or code '{order_identifier}'. Please check and try again.")
        return redirect('order_lookup')

    context = {
        'order': order,
        'items': order.items.select_related('menu_item').all(),
    }
    return render(request, 'restaurant/order_detail.html', context)


def api_order_status(request, order_identifier):
    """JSON endpoint for polling order status in real time."""
    order = None
    if order_identifier.isdigit():
        order = Order.objects.filter(id=int(order_identifier)).first()
    if not order:
        order = Order.objects.filter(order_code__iexact=order_identifier).first()

    if not order:
        return JsonResponse({'success': False, 'error': 'Order not found'}, status=404)

    return JsonResponse({
        'success': True,
        'id': order.id,
        'order_code': order.order_code,
        'status': order.status,
        'progress_percentage': order.progress_percentage,
        'badge_color': order.badge_color,
        'updated_at': order.updated_at.strftime('%H:%M:%S'),
    })


def kitchen_dashboard_view(request):
    """Staff dashboard for kitchen workflow and order management."""
    status_filter = request.GET.get('status', 'active')

    orders_query = Order.objects.prefetch_related('items__menu_item').all()

    if status_filter == 'active':
        orders = orders_query.exclude(status=Order.STATUS_COMPLETED).order_by('created_at')
    elif status_filter in [Order.STATUS_RECEIVED, Order.STATUS_PREPARING, Order.STATUS_READY, Order.STATUS_COMPLETED]:
        orders = orders_query.filter(status=status_filter).order_by('-created_at' if status_filter == Order.STATUS_COMPLETED else 'created_at')
    else:
        orders = orders_query.order_by('-created_at')

    # Status counts for header metrics
    counts = {
        'received': Order.objects.filter(status=Order.STATUS_RECEIVED).count(),
        'preparing': Order.objects.filter(status=Order.STATUS_PREPARING).count(),
        'ready': Order.objects.filter(status=Order.STATUS_READY).count(),
        'completed': Order.objects.filter(status=Order.STATUS_COMPLETED).count(),
        'total_active': Order.objects.exclude(status=Order.STATUS_COMPLETED).count(),
    }

    context = {
        'orders': orders,
        'status_filter': status_filter,
        'counts': counts,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'restaurant/kitchen_dashboard.html', context)


@require_POST
def kitchen_update_status(request, order_id):
    """Action to advance or update order status from kitchen dashboard."""
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('status')

    valid_statuses = [s[0] for s in Order.STATUS_CHOICES]
    if new_status in valid_statuses:
        order.status = new_status
        order.save()
        messages.success(request, f"Order #{order.id} ({order.order_code}) updated to '{new_status}'.")
    else:
        messages.error(request, "Invalid status update requested.")

    # Return JSON if requested via AJAX fetch
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({
            'success': True,
            'order_id': order.id,
            'new_status': order.status,
            'badge_color': order.badge_color,
            'progress_percentage': order.progress_percentage
        })

    next_url = request.POST.get('next', 'kitchen_dashboard')
    return redirect(next_url)
