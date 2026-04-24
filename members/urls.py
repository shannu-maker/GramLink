from django.urls import path
from . import views

def lazy_search_products_by_image(request, *args, **kwargs):
    from .search_views import search_products_by_image
    return search_products_by_image(request, *args, **kwargs)


def lazy_search_products_by_text_image(request, *args, **kwargs):
    from .search_views import search_products_by_text_image
    return search_products_by_text_image(request, *args, **kwargs)


def lazy_debug_models(request, *args, **kwargs):
    from .search_views import debug_models
    return debug_models(request, *args, **kwargs)


def lazy_search_page(request, *args, **kwargs):
    from .search_views import search_page
    return search_page(request, *args, **kwargs)


urlpatterns = [
    # Shopkeeper URLs
    path('shopkeeper/login/', views.shopkeeper_login, name='shopkeeper_login'),
    path('shopkeeper/register/', views.shopkeeper_register, name='shopkeeper_register'),
    path('shopkeeper/dashboard/', views.shopkeeper_dashboard, name='shopkeeper_dashboard'),
    path('shopkeeper/add-product/', views.add_product, name='add_product'),
    path('shopkeeper/edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('shopkeeper/delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('shopkeeper/update-order/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('shopkeeper/product/add/', views.add_product, name='add_product'),
    path('shopkeeper/product/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('shopkeeper/product/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('shopkeeper/requests/', views.shopkeeper_requests, name='shopkeeper_requests'),
    path('shopkeeper/requests/<int:request_id>/resolve/', views.resolve_request, name='resolve_request'),
    path('shopkeeper/close/', views.close_shop, name='close_shop'),
    path('shopkeeper/open/', views.open_shop, name='open_shop'),

    # Customer URLs
    path('customer/login/', views.customer_login, name='customer_login'),
    path('customer/register/', views.customer_register, name='customer_register'),
    path('customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('customer/cart/', views.customer_cart, name='customer_cart'),
    path('customer/orders/', views.customer_orders, name='customer_orders'),
    path('customer/checkout/', views.checkout, name='checkout'),
    path('customer/reorder/', views.reorder_last_order, name='reorder_last_order'),
    path('customer/reorder/<int:order_id>/', views.reorder_order, name='reorder_order'),
    path('customer/request-product/<int:shopkeeper_id>/', views.request_product_form, name='request_product_form'),

    # Delivery Partner URLs
    path('delivery/login/', views.delivery_login, name='delivery_login'),
    path('delivery/register/', views.delivery_register, name='delivery_register'),
    path('delivery/dashboard/', views.delivery_dashboard, name='delivery_dashboard'),
    path('delivery/accept-order/<int:order_id>/', views.accept_delivery_order, name='accept_delivery_order'),
    path('delivery/update-status/<int:order_id>/', views.update_delivery_status, name='update_delivery_status'),

    # Logout
    path('logout/', views.logout_view, name='logout'),
    
    # AI Chat (removed)

    # New Bot APIs for conversational auth
    path('api/shopkeeper/login/', views.api_shopkeeper_login, name='api_shopkeeper_login'),
    path('api/shopkeeper/register/', views.api_shopkeeper_register, name='api_shopkeeper_register'),
    path('api/delivery/login/', views.api_delivery_login, name='api_delivery_login'),
    path('api/delivery/register/', views.api_delivery_register, name='api_delivery_register'),

    # Test dashboard for debugging
    path('test-upload/', views.test_upload_page, name='test_upload'),

    # Home route for root URL
    path('', views.home, name='home'),

    # JSON APIs for Bot
    path('api/customer/login/', views.api_customer_login, name='api_customer_login'),
    path('api/customer/register/', views.api_customer_register, name='api_customer_register'),
    path('api/products/', views.api_products, name='api_products'),
    
    # API Endpoints for Location Data
    path('api/states/', views.api_states, name='api_states'),
    path('api/districts/<int:state_id>/', views.api_districts, name='api_districts'),
    path('api/mandals/<int:district_id>/', views.api_mandals, name='api_mandals'),
    path('api/villages/<int:mandal_id>/', views.api_villages, name='api_villages'),
    
    # Price History API
    path('api/product/<int:product_id>/price-history/', views.product_price_history, name='product_price_history'),
    
    # Search APIs (lazy import avoids heavy modules during checks)
    path('api/search/image/', lazy_search_products_by_image, name='search_products_by_image'),
    path('api/search/text-image/', lazy_search_products_by_text_image, name='search_products_by_text_image'),
    path('api/debug/models/', lazy_debug_models, name='debug_models'),
    path('search/', lazy_search_page, name='search_page'),
]
