from django.urls import path
from . import views

urlpatterns = [
    # Customer ordering & menu
    path('', views.menu_view, name='menu'),
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    
    # Order tracking
    path('track/', views.order_lookup_view, name='order_lookup'),
    path('track/<str:order_identifier>/', views.order_detail_view, name='order_detail'),

    # Kitchen staff dashboard
    path('kitchen/', views.kitchen_dashboard_view, name='kitchen_dashboard'),
    path('kitchen/order/<int:order_id>/update-status/', views.kitchen_update_status, name='kitchen_update_status'),

    # APIs for dynamic Cart & Live Polling
    path('api/cart/update/', views.api_update_cart, name='api_update_cart'),
    path('api/cart/sync/', views.api_sync_local_storage, name='api_sync_cart'),
    path('api/order-status/<str:order_identifier>/', views.api_order_status, name='api_order_status'),
]
