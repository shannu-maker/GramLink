from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password, check_password
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from .models import Shopkeeper, Customer, DeliveryPartner, Product, Order, OrderItem, PriceHistory, State, District, Mandal, Village, ProductRequest
from datetime import date
import json
from datetime import datetime
 

# --- Shopkeeper Views ---

def home(request):
    return render(request, 'home.html')

def shopkeeper_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            shopkeeper = Shopkeeper.objects.get(email=email)
            if shopkeeper.check_password(password):
                # Store shopkeeper info in session
                request.session['shopkeeper_id'] = shopkeeper.id
                request.session['user_type'] = 'shopkeeper'
                messages.success(request, 'Login successful!')
                return redirect('shopkeeper_dashboard')
            else:
                messages.error(request, 'Invalid credentials')
        except Shopkeeper.DoesNotExist:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'shopkeeper/login.html')

def shopkeeper_register(request):
    if request.method == 'POST':
        shop_name = request.POST.get('shop_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        address = request.POST.get('address')
        village_id = request.POST.get('village')
        
        # Check if shopkeeper already exists
        if Shopkeeper.objects.filter(email=email).exists():
            messages.error(request, 'A shop with this email already exists.')
            return render(request, 'shopkeeper/register.html')
        
        # Validate village selection
        if not village_id:
            messages.error(request, 'Please select your location (State, District, Mandal, Village).')
            return render(request, 'shopkeeper/register.html')
        
        # Create new shopkeeper
        shopkeeper = Shopkeeper.objects.create_user(
            email=email,
            name=shop_name,
            address=address,
            password=password,
            village_id=village_id
        )
        
        messages.success(request, 'Shop registered successfully! Please login.')
        return redirect('shopkeeper_login')
    
    return render(request, 'shopkeeper/register.html')

def shopkeeper_dashboard(request):
    # Check if logged in as shopkeeper
    if 'shopkeeper_id' not in request.session or request.session.get('user_type') != 'shopkeeper':
        messages.error(request, 'Please login to access dashboard.')
        return redirect('shopkeeper_login')
    
    try:
        shopkeeper_id = request.session['shopkeeper_id']
        shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
        
        # Fetch products and orders for this shopkeeper
        products = Product.objects.filter(shopkeeper=shopkeeper)
        orders = Order.objects.filter(shopkeeper=shopkeeper).order_by('-date')
        # Recent product requests for this shopkeeper
        shop_requests = ProductRequest.objects.filter(shopkeeper=shopkeeper).order_by('-created_at')[:10]
        
        # Count pending orders specifically
        pending_orders_count = orders.filter(status='pending').count()
        
        # Compute closure days remaining
        days_remaining = None
        if shopkeeper.closed_until:
            try:
                delta = (shopkeeper.closed_until - date.today()).days
                if delta >= 0:
                    days_remaining = delta
            except Exception:
                days_remaining = None

        context = {
            'shopkeeper': shopkeeper,
            'products': products,
            'orders': orders,
            'pending_orders_count': pending_orders_count,
            'today': date.today(),
            'days_remaining': days_remaining,
            'shop_requests': shop_requests,
        }
        
        return render(request, 'shopkeeper/dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f'Dashboard error: {str(e)}')
        return redirect('shopkeeper_login')

def add_product(request):
    """Handle product creation for shopkeepers"""
    
    # Check if logged in as shopkeeper
    if 'shopkeeper_id' not in request.session or request.session.get('user_type') != 'shopkeeper':
        messages.error(request, 'Please login as shopkeeper to add products.')
        return redirect('shopkeeper_login')
    
    if request.method == 'POST':
        try:
            shopkeeper_id = request.session['shopkeeper_id']
            shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
            
            # Get form data
            name = request.POST.get('name')
            price = request.POST.get('price')
            quantity = request.POST.get('quantity')
            image = request.FILES.get('image')
            description = request.POST.get('description', '')
            category = request.POST.get('category', 'other')
            
            # Validate required fields
            if not name or not price or not quantity:
                messages.error(request, 'Please fill in all required fields.')
                return redirect('shopkeeper_dashboard')
            
            # Create new product
            product = Product.objects.create(
                shopkeeper=shopkeeper,
                name=name,
                price=float(price),
                quantity=quantity,
                image=image,
                description=description,
                category=category
            )
            
            messages.success(request, f'Product "{name}" added successfully!')
            
        except ValueError as e:
            messages.error(request, 'Please enter a valid price.')
        except Exception as e:
            messages.error(request, f'Error adding product: {str(e)}')
    
    return redirect('shopkeeper_dashboard')

def edit_product(request, product_id):
    
    # Check if logged in as shopkeeper
    if 'shopkeeper_id' not in request.session or request.session.get('user_type') != 'shopkeeper':
        messages.error(request, 'Please login as shopkeeper to edit products.')
        return redirect('shopkeeper_login')
    
    # Get the product and verify ownership
    shopkeeper_id = request.session['shopkeeper_id']
    shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
    product = get_object_or_404(Product, id=product_id, shopkeeper=shopkeeper)
    
    if request.method == 'POST':
        try:
            # Get form data
            name = request.POST.get('name')
            price = request.POST.get('price')
            quantity = request.POST.get('quantity')
            description = request.POST.get('description', '')
            image = request.FILES.get('image')
            category = request.POST.get('category', 'other')
            
            # Validate required fields
            if not name or not price or not quantity:
                messages.error(request, 'Please fill in all required fields.')
                return redirect('edit_product', product_id=product_id)
            
            # Update product
            product.name = name
            product.price = float(price)
            product.quantity = quantity
            product.description = description
            product.category = category
            if image:  # Only update image if a new one was provided
                product.image = image
            product.save()
            
            messages.success(request, f'Product "{name}" updated successfully!')
            return redirect('shopkeeper_dashboard')
            
        except ValueError:
            messages.error(request, 'Please enter a valid price.')
            return redirect('edit_product', product_id=product_id)
    
    # For GET request, show the edit form
    return render(request, 'shopkeeper/edit_product.html', {'product': product})

def delete_product(request, product_id):
    """Handle product deletion for shopkeepers"""
    
    # Check if logged in as shopkeeper
    if 'shopkeeper_id' not in request.session or request.session.get('user_type') != 'shopkeeper':
        messages.error(request, 'Please login as shopkeeper to delete products.')
        return redirect('shopkeeper_login')
    
    if request.method == 'POST':
        try:
            shopkeeper_id = request.session['shopkeeper_id']
            shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
            
            # Get the product and verify ownership
            product = get_object_or_404(Product, id=product_id, shopkeeper=shopkeeper)
            product_name = product.name
            
            # Delete the product
            product.delete()
            
            messages.success(request, f'Product "{product_name}" deleted successfully!')
            
        except Exception as e:
            messages.error(request, f'Error deleting product: {str(e)}')
    
    return redirect('shopkeeper_dashboard')

def update_order_status(request, order_id):
    """Handle order status updates for shopkeepers"""
    
    # Check if logged in as shopkeeper
    if 'shopkeeper_id' not in request.session or request.session.get('user_type') != 'shopkeeper':
        messages.error(request, 'Please login as shopkeeper to update orders.')
        return redirect('shopkeeper_login')
    
    if request.method == 'POST':
        try:
            shopkeeper_id = request.session['shopkeeper_id']
            shopkeeper = Shopkeeper.objects.get(id=shopkeeper_id)
            
            # Get the order and verify ownership
            order = get_object_or_404(Order, id=order_id, shopkeeper=shopkeeper)
            new_status = request.POST.get('status')
            
            # Validate the new status
            valid_statuses = ['pending', 'confirmed', 'ready', 'assigned', 'out_for_delivery', 'delivered', 'cancelled']
            if new_status not in valid_statuses:
                messages.error(request, 'Invalid order status.')
                return redirect('shopkeeper_dashboard')
            
            # Update the order status
            order.status = new_status
            order.save()
            
            # Provide appropriate success message
            if new_status == 'confirmed':
                messages.success(request, f'Order #{order_id} confirmed successfully!')
            elif new_status == 'ready':
                messages.success(request, f'Order #{order_id} marked as ready for pickup!')
            elif new_status == 'cancelled':
                messages.success(request, f'Order #{order_id} cancelled successfully.')
            else:
                messages.success(request, f'Order #{order_id} status updated to {new_status.title()}.')
            
        except Exception as e:
            messages.error(request, f'Error updating order status: {str(e)}')
    
    return redirect('shopkeeper_dashboard')

# --- Customer Views ---

def customer_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            customer = Customer.objects.get(email=email)
            if check_password(password, customer.password):
                # Store customer info in session
                request.session['customer_id'] = customer.id
                request.session['user_type'] = 'customer'
                messages.success(request, 'Login successful!')
                return redirect('customer_dashboard')
            else:
                messages.error(request, 'Invalid credentials')
        except Customer.DoesNotExist:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'customer/login.html')

def customer_register(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        village_id = request.POST.get('village')
        
        # Check if customer already exists
        if Customer.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists.')
            return render(request, 'customer/register.html')
        
        # Validate village selection
        if not village_id:
            messages.error(request, 'Please select your location (State, District, Mandal, Village).')
            return render(request, 'customer/register.html')
        
        # Create new customer
        customer = Customer.objects.create(
            name=full_name,
            email=email,
            phone=phone,
            password=make_password(password),
            village_id=village_id
        )
        
        messages.success(request, 'Account created successfully! Please login.')
        return redirect('home')
    
    return render(request, 'customer/register.html')

def customer_dashboard(request):
    # Check if logged in as customer
    if 'customer_id' not in request.session or request.session.get('user_type') != 'customer':
        messages.error(request, 'Please login to access dashboard.')
        return redirect('customer_login')
    
    try:
        customer_id = request.session['customer_id']
        customer = Customer.objects.get(id=customer_id)
        
        # Fetch all products from all shopkeepers
        # Filter products by customer's village if customer is logged in
        if customer.village:
            products = Product.objects.filter(
                shopkeeper__village=customer.village,
            ).order_by('-id')
        else:
            products = Product.objects.all().order_by('-id')
        
        # Group products by category for category-based display
        products_by_category = {}
        for product in products:
            category = product.category
            if category not in products_by_category:
                products_by_category[category] = []
            products_by_category[category].append(product)

        # Build map of shopkeeper -> days remaining if shop is closed
        for p in products:
            sk = p.shopkeeper
            if not sk:
                continue
            # Compute and attach attribute on shopkeeper for template use
            days_remaining = None
            if sk.closed_until and sk.closed_until >= date.today():
                try:
                    delta = (sk.closed_until - date.today()).days
                    if delta >= 0:
                        days_remaining = delta
                except Exception:
                    days_remaining = None
            try:
                setattr(sk, 'closed_days_remaining', days_remaining)
            except Exception:
                pass

        # Fetch orders for this customer
        orders = Order.objects.filter(customer=customer).order_by('-date')
        # Fetch recent product requests by this customer
        customer_requests = ProductRequest.objects.filter(customer=customer).order_by('-created_at')[:10]
        
        context = {
            'customer': customer,
            'products': products,
            'products_by_category': products_by_category,
            'orders': orders,
            'today': date.today(),
            'customer_requests': customer_requests,
        }
        
        return render(request, 'customer/dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f'Dashboard error: {str(e)}')
        return redirect('customer_login')

def customer_cart(request):
    # Check if logged in as customer
    if 'customer_id' not in request.session or request.session.get('user_type') != 'customer':
        messages.error(request, 'Please login to access cart.')
        return redirect('customer_login')
    
    try:
        customer = Customer.objects.get(id=request.session['customer_id'])
    except Customer.DoesNotExist:
        messages.error(request, 'Customer account not found.')
        return redirect('customer_login')

    context = {
        'cart_items': [],  # kept for compatibility, items are client-side
        'customer': customer,
    }
    return render(request, 'customer/cart.html', context)

def customer_orders(request):
    # Check if logged in as customer
    if 'customer_id' not in request.session or request.session.get('user_type') != 'customer':
        messages.error(request, 'Please login to access orders.')
        return redirect('customer_login')
    
    customer_id = request.session['customer_id']
    orders = Order.objects.filter(customer_id=customer_id).order_by('-date')
    
    context = {
        'orders': orders,
    }
    return render(request, 'customer/orders.html', context)


# --- Product Request Flows ---
def request_product_form(request, shopkeeper_id):
    # Ensure customer is logged in
    if 'customer_id' not in request.session or request.session.get('user_type') != 'customer':
        messages.error(request, 'Please login to request a product.')
        return redirect('customer_login')

    shopkeeper = get_object_or_404(Shopkeeper, id=shopkeeper_id)
    customer = get_object_or_404(Customer, id=request.session['customer_id'])

    if request.method == 'POST':
        product_name = (request.POST.get('product_name') or '').strip()
        details = (request.POST.get('details') or '').strip()
        if not product_name:
            messages.error(request, 'Please enter the product name.')
        else:
            ProductRequest.objects.create(
                customer=customer,
                shopkeeper=shopkeeper,
                product_name=product_name,
                details=details,
            )
            messages.success(request, 'Your request has been sent to the shopkeeper.')
            return redirect('customer_dashboard')

    # Recent requests by this customer to this shopkeeper
    recent_requests = ProductRequest.objects.filter(customer=customer, shopkeeper=shopkeeper).order_by('-created_at')[:20]

    return render(request, 'customer/request_product.html', {
        'shopkeeper': shopkeeper,
        'customer': customer,
        'recent_requests': recent_requests,
    })


def shopkeeper_requests(request):
    # Ensure shopkeeper is logged in
    if 'shopkeeper_id' not in request.session or request.session.get('user_type') != 'shopkeeper':
        messages.error(request, 'Please login as shopkeeper to view requests.')
        return redirect('shopkeeper_login')

    shopkeeper = get_object_or_404(Shopkeeper, id=request.session['shopkeeper_id'])
    requests_qs = ProductRequest.objects.filter(shopkeeper=shopkeeper)
    return render(request, 'shopkeeper/requests.html', {
        'shopkeeper': shopkeeper,
        'requests': requests_qs,
    })


def resolve_request(request, request_id):
    # Ensure shopkeeper is logged in
    if 'shopkeeper_id' not in request.session or request.session.get('user_type') != 'shopkeeper':
        messages.error(request, 'Please login as shopkeeper to manage requests.')
        return redirect('shopkeeper_login')

    req = get_object_or_404(ProductRequest, id=request_id, shopkeeper_id=request.session['shopkeeper_id'])
    if request.method == 'POST':
        req.resolved = True
        req.save()
        messages.success(request, 'Request marked as resolved.')
    return redirect('shopkeeper_requests')


# --- Shop Closure Management ---
def close_shop(request):
    # Ensure shopkeeper is logged in
    if 'shopkeeper_id' not in request.session or request.session.get('user_type') != 'shopkeeper':
        messages.error(request, 'Please login as shopkeeper to manage shop status.')
        return redirect('shopkeeper_login')

    shopkeeper = get_object_or_404(Shopkeeper, id=request.session['shopkeeper_id'])

    if request.method == 'POST':
        days = request.POST.get('days')
        try:
            days_int = int(days)
            if days_int < 1:
                raise ValueError('days must be positive')
            shopkeeper.closed_until = date.today().fromordinal(date.today().toordinal() + days_int)
            shopkeeper.save()
            if days_int == 1:
                messages.success(request, 'Shop closed for 1 day.')
            else:
                messages.success(request, f'Shop closed for {days_int} days.')
        except Exception:
            messages.error(request, 'Please enter a valid number of days.')
        return redirect('shopkeeper_dashboard')

    return render(request, 'shopkeeper/close_shop.html', {'shopkeeper': shopkeeper})


def open_shop(request):
    # Ensure shopkeeper is logged in
    if 'shopkeeper_id' not in request.session or request.session.get('user_type') != 'shopkeeper':
        messages.error(request, 'Please login as shopkeeper to manage shop status.')
        return redirect('shopkeeper_login')

    shopkeeper = get_object_or_404(Shopkeeper, id=request.session['shopkeeper_id'])
    if request.method == 'POST':
        shopkeeper.closed_until = None
        shopkeeper.save()
        messages.success(request, 'Shop is now open.')
        return redirect('shopkeeper_dashboard')

    return render(request, 'shopkeeper/open_shop.html', {'shopkeeper': shopkeeper})

def reorder_last_order(request):
    # Ensure customer is logged in
    if 'customer_id' not in request.session or request.session.get('user_type') != 'customer':
        messages.error(request, 'Please login to reorder.')
        return redirect('customer_login')

    try:
        customer_id = request.session['customer_id']
        last_order = Order.objects.filter(customer_id=customer_id).order_by('-date').first()
        if not last_order:
            messages.error(request, 'No previous orders found to reorder.')
            return redirect('customer_dashboard')

        # Build cart items compatible with existing cart structure (localStorage)
        cart_items = []
        for item in last_order.items.select_related('product').all():
            if item.product is None:
                continue
            cart_items.append({
                'id': item.product.id,
                'name': item.product.name,
                'price': float(item.product.price),
                'quantity': int(item.quantity),
                'shop': last_order.shopkeeper.name,
            })

        if not cart_items:
            messages.error(request, 'Products from the last order are no longer available.')
            return redirect('customer_dashboard')

        # Render a small page that sets localStorage cart then redirects to cart/checkout
        return render(request, 'customer/reorder_redirect.html', {
            'cart_json': json.dumps(cart_items)
        })

    except Exception as e:
        messages.error(request, f'Unable to reorder: {str(e)}')
        return redirect('customer_dashboard')

def reorder_order(request, order_id):
    # Ensure customer is logged in
    if 'customer_id' not in request.session or request.session.get('user_type') != 'customer':
        messages.error(request, 'Please login to reorder.')
        return redirect('customer_login')

    try:
        customer_id = request.session['customer_id']
        # Ensure the order belongs to the current customer
        order = Order.objects.filter(customer_id=customer_id, id=order_id).first()
        if not order:
            messages.error(request, 'Order not found.')
            return redirect('customer_orders')

        # Build cart items compatible with existing cart structure (localStorage)
        cart_items = []
        for item in order.items.select_related('product').all():
            if item.product is None:
                # Product could have been deleted; fallback to stored name without id
                # Skip items without a current product id as checkout expects id
                continue
            cart_items.append({
                'id': item.product.id,
                'name': item.product.name,
                'price': float(item.product.price),
                'quantity': int(item.quantity),
                'shop': order.shopkeeper.name,
            })

        if not cart_items:
            messages.error(request, 'Products from this order are no longer available to reorder.')
            return redirect('customer_orders')

        # Render a small page that sets localStorage cart then redirects to cart/checkout
        return render(request, 'customer/reorder_redirect.html', {
            'cart_json': json.dumps(cart_items)
        })

    except Exception as e:
        messages.error(request, f'Unable to reorder: {str(e)}')
        return redirect('customer_orders')

def checkout(request):
    """Handle checkout process and create orders"""
    
    # Check if logged in as customer
    if 'customer_id' not in request.session or request.session.get('user_type') != 'customer':
        messages.error(request, 'Please login to place orders.')
        return redirect('customer_login')
    
    if request.method == 'POST':
        try:
            customer_id = request.session['customer_id']
            customer = Customer.objects.get(id=customer_id)
            
            # Get form data
            full_name = request.POST.get('full_name')
            phone = request.POST.get('phone')
            address = request.POST.get('address')
            payment_method = request.POST.get('payment_method')
            instructions = request.POST.get('instructions', '')
            cart_data = request.POST.get('cart_data')
            
            # Validate required fields
            if not all([full_name, phone, address, payment_method, cart_data]):
                messages.error(request, 'Please fill in all required fields.')
                return redirect('customer_dashboard')
            
            # Parse cart data
            try:
                cart_items = json.loads(cart_data)
                if not cart_items:
                    messages.error(request, 'Your cart is empty.')
                    return redirect('customer_dashboard')
            except json.JSONDecodeError:
                messages.error(request, 'Invalid cart data.')
                return redirect('customer_dashboard')
            
            # Group items by shopkeeper to create separate orders
            orders_by_shop = {}
            for item in cart_items:
                try:
                    product = Product.objects.get(id=item['id'])
                    shopkeeper = product.shopkeeper
                    
                    if shopkeeper.id not in orders_by_shop:
                        orders_by_shop[shopkeeper.id] = {
                            'shopkeeper': shopkeeper,
                            'items': [],
                            'total': 0
                        }
                    
                    item_total = float(item['price']) * int(item['quantity'])
                    orders_by_shop[shopkeeper.id]['items'].append({
                        'product': product,
                        'quantity': int(item['quantity']),
                        'price': float(item['price']),
                        'total': item_total
                    })
                    orders_by_shop[shopkeeper.id]['total'] += item_total
                    
                except Product.DoesNotExist:
                    continue
            
            # Create orders for each shopkeeper
            created_orders = []
            for shop_data in orders_by_shop.values():
                # Create the order
                order = Order.objects.create(
                    customer=customer,
                    shopkeeper=shop_data['shopkeeper'],
                    delivery_name=full_name,
                    delivery_phone=phone,
                    delivery_address=address,
                    payment_method=payment_method,
                    special_instructions=instructions,
                    total_amount=shop_data['total'],
                    status='pending',
                    date=datetime.now()
                )
                
                # Create order items
                for item_data in shop_data['items']:
                    OrderItem.objects.create(
                        order=order,
                        product=item_data['product'],  # can be null later if deleted
                        product_name=item_data['product'].name,  # store name permanently
                        quantity=item_data['quantity'],
                        price=item_data['product'].price  # store price at time of order
                    )

                
                created_orders.append(order)
            
            # Clear the cart (this will be done via JavaScript)
            order_count = len(created_orders)
            total_amount = sum(order.total_amount for order in created_orders)
            
            if order_count == 1:
                messages.success(request, f'Order placed successfully! Order total: ₹{total_amount:.2f}')
            else:
                messages.success(request, f'{order_count} orders placed successfully! Total: ₹{total_amount:.2f}')
            
            # Redirect to orders page so the user can see their order
            return redirect('customer_orders')
            
        except Customer.DoesNotExist:
            messages.error(request, 'Customer account not found.')
            return redirect('customer_login')
        except Exception as e:
            messages.error(request, f'Error processing checkout: {str(e)}')
            return redirect('customer_dashboard')
    
    # If not POST, redirect to dashboard
    return redirect('customer_dashboard')

# --- Delivery Partner Views ---

def delivery_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            delivery_partner = DeliveryPartner.objects.get(email=email)
            if check_password(password, delivery_partner.password):
                # Store delivery partner info in session
                request.session['delivery_id'] = delivery_partner.id
                request.session['user_type'] = 'delivery'
                messages.success(request, 'Login successful!')
                return redirect('delivery_dashboard')
            else:
                messages.error(request, 'Invalid credentials')
        except DeliveryPartner.DoesNotExist:
            messages.error(request, 'Invalid credentials')
    
    return render(request, 'delivery/login.html')

def delivery_register(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        vehicle_type = request.POST.get('vehicle_type')
        village_id = request.POST.get('village')
        
        # Check if delivery partner already exists
        if DeliveryPartner.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists.')
            return render(request, 'delivery/register.html')
        
        # Validate village selection
        if not village_id:
            messages.error(request, 'Please select your location (State, District, Mandal, Village).')
            return render(request, 'delivery/register.html')
        
        # Create new delivery partner
        delivery_partner = DeliveryPartner.objects.create(
            name=full_name,
            email=email,
            vehicle=vehicle_type,
            password=make_password(password),
            village_id=village_id
        )
        
        messages.success(request, 'Application submitted successfully! Please login.')
        return redirect('home')
    
    return render(request, 'delivery/register.html')

def delivery_dashboard(request):
    # Check if logged in as delivery partner
    if 'delivery_id' not in request.session or request.session.get('user_type') != 'delivery':
        messages.error(request, 'Please login to access dashboard.')
        return redirect('delivery_login')
    
    try:
        delivery_id = request.session['delivery_id']
        delivery_partner = DeliveryPartner.objects.get(id=delivery_id)
        
        # Fetch available orders for delivery (orders that are ready or confirmed)
        available_orders = Order.objects.filter(
            status__in=['confirmed', 'ready'],
            shopkeeper__village=delivery_partner.village # Filter by delivery partner's village
        ).order_by('-date')
        
        # Fetch orders assigned to this delivery partner
        assigned_orders = Order.objects.filter(
            delivery_partner=delivery_partner,
            shopkeeper__village=delivery_partner.village # Ensure assigned orders are also from their village
        ).order_by('-date')
        
        context = {
            'delivery_partner': delivery_partner,
            'available_orders': available_orders,
            'assigned_orders': assigned_orders,
        }
        
        return render(request, 'delivery/dashboard.html', context)
        
    except Exception as e:
        messages.error(request, f'Dashboard error: {str(e)}')
        return redirect('delivery_login')

def accept_delivery_order(request, order_id):
    """Handle delivery partner accepting an order for delivery"""
    
    # Check if logged in as delivery partner
    if 'delivery_id' not in request.session or request.session.get('user_type') != 'delivery':
        messages.error(request, 'Please login as delivery partner to accept orders.')
        return redirect('delivery_login')
    
    if request.method == 'POST':
        try:
            delivery_id = request.session['delivery_id']
            delivery_partner = DeliveryPartner.objects.get(id=delivery_id)
            
            # Get the order and verify it's available for delivery
            order = Order.objects.get(id=order_id)
            
            # Check if order is available for delivery
            if order.status not in ['ready']:
                messages.error(request, 'This order is not available for delivery.')
                return redirect('delivery_dashboard')
            
            # Check if order is already assigned to another delivery partner
            if order.delivery_partner and order.delivery_partner != delivery_partner:
                messages.error(request, 'This order is already assigned to another delivery partner.')
                return redirect('delivery_dashboard')
            
            # Assign the order to this delivery partner
            order.delivery_partner = delivery_partner
            order.status = 'assigned'
            order.save()
            
            messages.success(request, f'Order #{order_id} accepted successfully! You can now start the delivery.')
            
        except Order.DoesNotExist:
            messages.error(request, 'Order not found.')
        except DeliveryPartner.DoesNotExist:
            messages.error(request, 'Delivery partner account not found.')
        except Exception as e:
            messages.error(request, f'Error accepting order: {str(e)}')
    
    return redirect('delivery_dashboard')

def update_delivery_status(request, order_id):
    """Handle delivery status updates (start delivery, mark delivered)"""
    
    # Check if logged in as delivery partner
    if 'delivery_id' not in request.session or request.session.get('user_type') != 'delivery':
        messages.error(request, 'Please login as delivery partner to update delivery status.')
        return redirect('delivery_login')
    
    if request.method == 'POST':
        try:
            delivery_id = request.session['delivery_id']
            delivery_partner = DeliveryPartner.objects.get(id=delivery_id)
            
            # Get the order and verify it's assigned to this delivery partner
            order = Order.objects.get(id=order_id, delivery_partner=delivery_partner)
            new_status = request.POST.get('status')
            
            # Validate the new status
            valid_delivery_statuses = ['assigned', 'out_for_delivery', 'delivered']
            if new_status not in valid_delivery_statuses:
                messages.error(request, 'Invalid delivery status.')
                return redirect('delivery_dashboard')

            
            # Update the order status
            old_status = order.status
            order.status = new_status
            order.save()
            
            # Provide appropriate success message
            if new_status == 'out_for_delivery':
                messages.success(request, f'Order #{order_id} marked as out for delivery!')
            elif new_status == 'delivered':
                messages.success(request, f'Order #{order_id} marked as delivered successfully!')
            else:
                messages.success(request, f'Order #{order_id} status updated to {new_status.title()}.')
            
        except Order.DoesNotExist:
            messages.error(request, 'Order not found or not assigned to you.')
        except Exception as e:
            messages.error(request, f'Error updating delivery status: {str(e)}')
    
    return redirect('delivery_dashboard')

# --- Test Dashboard (for debugging) ---
def test_upload_page(request):
    """Simple test page for debugging image upload"""
    return render(request, 'test_upload.html')

# --- Logout view (shared) ---

from django.contrib.auth import logout

def logout_view(request):
    # Clear all session data
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

# --- Lightweight JSON APIs for Bot ---

@csrf_exempt
def api_customer_login(request):
    """JSON login for customers; establishes session on success."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body.decode('utf-8'))
        email = (data.get('email') or '').strip()
        password = data.get('password') or ''
        if not email or not password:
            return JsonResponse({'success': False, 'error': 'Email and password are required'}, status=400)
        customer = Customer.objects.get(email=email)
        if not check_password(password, customer.password):
            return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=401)
        request.session['customer_id'] = customer.id
        request.session['user_type'] = 'customer'
        return JsonResponse({'success': True, 'customer': {'id': customer.id, 'name': customer.name, 'email': customer.email}})
    except Customer.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Account not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_customer_register(request):
    """JSON register for customers; creates account and logs in."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body.decode('utf-8'))
        name = (data.get('name') or '').strip()
        email = (data.get('email') or '').strip()
        phone = (data.get('phone') or '').strip()
        password = data.get('password') or ''
        village_id = data.get('village_id')

        if not all([name, email, phone, password, village_id]):
            return JsonResponse({'success': False, 'error': 'All fields are required'}, status=400)
        if Customer.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'error': 'Email already in use'}, status=409)
        customer = Customer.objects.create(name=name, email=email, phone=phone, password=make_password(password), village_id=village_id)
        request.session['customer_id'] = customer.id
        request.session['user_type'] = 'customer'
        return JsonResponse({'success': True, 'customer': {'id': customer.id, 'name': customer.name, 'email': customer.email, 'village_id': customer.village_id}})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def api_products(request):
    """Public JSON products API. Supports alphabetical list or shop-wise grouping and a simple search query."""
    mode = (request.GET.get('mode') or 'alphabetical').lower()
    query = (request.GET.get('q') or '').strip()
    customer_id = request.session.get('customer_id') # Get customer_id from session

    try:
        products_qs = Product.objects.select_related('shopkeeper')
        # Hide products for shops that are closed until a future date
        products_qs = products_qs.exclude(shopkeeper__closed_until__gte=date.today())

        # Filter products by customer's village if customer is logged in
        if customer_id:
            customer = Customer.objects.get(id=customer_id)
            if customer.village:
                # Filter products whose shopkeepers are in the same village as the customer
                products_qs = products_qs.filter(shopkeeper__village=customer.village)

        if query:
            # Simple contains search on product name and shop name
            products_qs = products_qs.filter(Q(name__icontains=query) | Q(shopkeeper__name__icontains=query))
        if mode == 'shopwise':
            # Group by shop; each group sorted by product name
            response_payload = []
            by_shop = {}
            for p in products_qs:
                shop_name = p.shopkeeper.name if p.shopkeeper else 'Unknown Shop'
                by_shop.setdefault(shop_name, []).append(p)
            for shop_name, shop_products in by_shop.items():
                shop_products_sorted = sorted(shop_products, key=lambda x: x.name.lower())
                response_payload.append({
                    'shop': shop_name,
                    'products': [
                        {
                            'id': sp.id,
                            'name': sp.name,
                            'price': float(sp.price),
                            'quantity': sp.quantity,
                            'description': sp.description,
                            'image_url': (sp.image.url if sp.image else ''),
                        }
                        for sp in shop_products_sorted
                    ]
                })
            # Sort groups by shop name for consistency
            response_payload.sort(key=lambda g: g['shop'].lower())
            return JsonResponse({'success': True, 'mode': 'shopwise', 'groups': response_payload})
        else:
            # Alphabetical list by product name
            products_sorted = products_qs.order_by('name')
            items = []
            for p in products_sorted:
                items.append({
                    'id': p.id,
                    'name': p.name,
                    'price': float(p.price),
                    'quantity': p.quantity,
                    'description': p.description,
                    'shop': (p.shopkeeper.name if p.shopkeeper else 'Unknown Shop'),
                    'image_url': (p.image.url if p.image else ''),
                })
            return JsonResponse({'success': True, 'mode': 'alphabetical', 'products': items})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)



@csrf_exempt
def api_shopkeeper_login(request):
	if request.method != 'POST':
		return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
	try:
		data = json.loads(request.body.decode('utf-8'))
		email = (data.get('email') or '').strip()
		password = data.get('password') or ''
		if not email or not password:
			return JsonResponse({'success': False, 'error': 'Email and password are required'}, status=400)
		shopkeeper = Shopkeeper.objects.get(email=email)
		if not shopkeeper.check_password(password):
			return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=401)
		request.session['shopkeeper_id'] = shopkeeper.id
		request.session['user_type'] = 'shopkeeper'
		return JsonResponse({'success': True, 'shopkeeper': {'id': shopkeeper.id, 'name': shopkeeper.name, 'email': shopkeeper.email}})
	except Shopkeeper.DoesNotExist:
		return JsonResponse({'success': False, 'error': 'Account not found'}, status=404)
	except Exception as e:
		return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_shopkeeper_register(request):
    """JSON register for shopkeepers; creates account and logs in."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body.decode('utf-8'))
        name = (data.get('name') or '').strip()
        email = (data.get('email') or '').strip()
        address = (data.get('address') or '').strip()
        password = data.get('password') or ''
        village_id = data.get('village_id') # Get village_id from request data

        if not all([name, email, address, password, village_id]):
            return JsonResponse({'success': False, 'error': 'All fields are required'}, status=400)
        if Shopkeeper.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'error': 'Email already in use'}, status=409)
        shopkeeper = Shopkeeper.objects.create_user(email=email, name=name, address=address, password=password, village_id=village_id)
        request.session['shopkeeper_id'] = shopkeeper.id
        request.session['user_type'] = 'shopkeeper'
        return JsonResponse({'success': True, 'shopkeeper': {'id': shopkeeper.id, 'name': shopkeeper.name, 'email': shopkeeper.email, 'village_id': shopkeeper.village_id}})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_delivery_login(request):
	if request.method != 'POST':
		return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
	try:
		data = json.loads(request.body.decode('utf-8'))
		email = (data.get('email') or '').strip()
		password = data.get('password') or ''
		if not email or not password:
			return JsonResponse({'success': False, 'error': 'Email and password are required'}, status=400)
		dp = DeliveryPartner.objects.get(email=email)
		if not check_password(password, dp.password):
			return JsonResponse({'success': False, 'error': 'Invalid credentials'}, status=401)
		request.session['delivery_id'] = dp.id
		request.session['user_type'] = 'delivery'
		return JsonResponse({'success': True, 'delivery': {'id': dp.id, 'name': dp.name, 'email': dp.email}})
	except DeliveryPartner.DoesNotExist:
		return JsonResponse({'success': False, 'error': 'Account not found'}, status=404)
	except Exception as e:
		return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def api_delivery_register(request):
	if request.method != 'POST':
		return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
	try:
		data = json.loads(request.body.decode('utf-8'))
		name = (data.get('name') or '').strip()
		email = (data.get('email') or '').strip()
		vehicle = (data.get('vehicle') or '').strip()
		password = data.get('password') or ''
		village_id = data.get('village_id')
		if not all([name, email, vehicle, password, village_id]):
			return JsonResponse({'success': False, 'error': 'All fields are required'}, status=400)
		if DeliveryPartner.objects.filter(email=email).exists():
			return JsonResponse({'success': False, 'error': 'Email already in use'}, status=409)
		dp = DeliveryPartner.objects.create(name=name, email=email, vehicle=vehicle, password=make_password(password), village_id=village_id)
		request.session['delivery_id'] = dp.id
		request.session['user_type'] = 'delivery'
		return JsonResponse({'success': True, 'delivery': {'id': dp.id, 'name': dp.name, 'email': dp.email, 'village_id': dp.village_id}})
	except Exception as e:
		return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def product_price_history(request, product_id):
    """Get price history for a product with analysis and recommendations"""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    
    try:
        product = get_object_or_404(Product, id=product_id)
        price_history = PriceHistory.objects.filter(product=product).order_by('timestamp')
        
        if not price_history.exists():
            return JsonResponse({
                'success': True,
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'current_price': float(product.price)
                },
                'price_history': [],
                'analysis': {
                    'message': 'No price history available for this product.',
                    'recommendation': 'This is a new product with no price history.',
                    'confidence': 'low'
                }
            })
        
        # Prepare price history data
        history_data = []
        prices = []
        dates = []
        
        for entry in price_history:
            history_data.append({
                'timestamp': entry.timestamp.isoformat(),
                'old_price': float(entry.old_price),
                'new_price': float(entry.new_price),
                'change': float(entry.price_change),
                'percentage_change': round(entry.percentage_change, 2),
                'reason': entry.change_reason
            })
            prices.append(float(entry.new_price))
            dates.append(entry.timestamp.isoformat())
        
        # Add current price to analysis
        current_price = float(product.price)
        prices.append(current_price)
        
        # Price analysis
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / len(prices)
        
        # Calculate price trend
        recent_prices = [float(entry.new_price) for entry in price_history[:3]]
        if len(recent_prices) >= 2:
            trend = "increasing" if recent_prices[0] > recent_prices[-1] else "decreasing"
        else:
            trend = "stable"
        
        # Generate recommendation
        recommendation = generate_price_recommendation(current_price, min_price, max_price, avg_price, trend)
        
        analysis = {
            'current_price': current_price,
            'min_price': min_price,
            'max_price': max_price,
            'avg_price': round(avg_price, 2),
            'price_range': round(max_price - min_price, 2),
            'trend': trend,
            'recommendation': recommendation['message'],
            'confidence': recommendation['confidence'],
            'savings_potential': recommendation['savings_potential']
        }
        
        return JsonResponse({
            'success': True,
            'product': {
                'id': product.id,
                'name': product.name,
                'current_price': current_price
            },
            'price_history': history_data,
            'analysis': analysis,
            'chart_data': {
                'prices': prices,
                'dates': dates
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def generate_price_recommendation(current_price, min_price, max_price, avg_price, trend):
    """Generate buying recommendation based on price analysis"""
    
    # Calculate how current price compares to historical data
    price_vs_min = ((current_price - min_price) / min_price) * 100 if min_price > 0 else 0
    price_vs_avg = ((current_price - avg_price) / avg_price) * 100 if avg_price > 0 else 0
    price_vs_max = ((current_price - max_price) / max_price) * 100 if max_price > 0 else 0
    
    # Determine recommendation
    if current_price <= min_price:
        recommendation = "Excellent time to buy! Current price is at or near the lowest it has ever been."
        confidence = "high"
        savings_potential = f"Up to {round(max_price - current_price, 2)} saved compared to highest price"
    elif current_price <= avg_price:
        if trend == "decreasing":
            recommendation = "Good time to buy! Price is below average and trending down."
            confidence = "high"
        else:
            recommendation = "Fair time to buy. Price is below average but may continue to rise."
            confidence = "medium"
        savings_potential = f"Up to {round(max_price - current_price, 2)} saved compared to highest price"
    elif current_price <= max_price * 0.8:  # Within 80% of max
        if trend == "decreasing":
            recommendation = "Consider waiting. Price is above average but trending down."
            confidence = "medium"
        else:
            recommendation = "Price is above average and rising. Consider waiting for a better deal."
            confidence = "medium"
        savings_potential = f"Could save up to {round(current_price - min_price, 2)} by waiting"
    else:  # Near or at max price
        recommendation = "Not recommended to buy now. Price is near historical high."
        confidence = "high"
        savings_potential = f"Could save up to {round(current_price - min_price, 2)} by waiting"
    
    return {
        'message': recommendation,
        'confidence': confidence,
        'savings_potential': savings_potential
    }

@csrf_exempt
def api_states(request):
    """API to return all states."""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    try:
        states = State.objects.all().order_by('name')
        data = [{'id': state.id, 'name': state.name} for state in states]
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
def api_districts(request, state_id):
    """API to return districts for a given state."""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    try:
        districts = District.objects.filter(state_id=state_id).order_by('name')
        data = [{'id': district.id, 'name': district.name} for district in districts]
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
def api_mandals(request, district_id):
    """API to return mandals for a given district."""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    try:
        mandals = Mandal.objects.filter(district_id=district_id).order_by('name')
        data = [{'id': mandal.id, 'name': mandal.name} for mandal in mandals]
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@csrf_exempt
def api_villages(request, mandal_id):
    """API to return villages for a given mandal."""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
    try:
        villages = Village.objects.filter(mandal_id=mandal_id).order_by('name')
        data = [{'id': village.id, 'name': village.name} for village in villages]
        return JsonResponse(data, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
