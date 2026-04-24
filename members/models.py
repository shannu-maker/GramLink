from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class ShopkeeperManager(BaseUserManager):
    def create_user(self, email, name, address, password=None, village_id=None):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, address=address)
        if village_id:
            user.village_id = village_id
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, address, password):
        user = self.create_user(email, name, address, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Shopkeeper(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    village = models.ForeignKey(
        'Village', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='shopkeepers'
    )
    # If set in the future, the shop is considered closed until this date (inclusive)
    closed_until = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='shopkeeper_set',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='shopkeeper_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    objects = ShopkeeperManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'address']

    def __str__(self):
        return self.email

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    password = models.CharField(max_length=128)
    village = models.ForeignKey(
        'Village', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='customers'
    )

class DeliveryPartner(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    vehicle = models.CharField(max_length=50)
    password = models.CharField(max_length=128)
    village = models.ForeignKey(
        'Village', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='delivery_partners'
    )

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('dairy', 'Dairy & Milk'),
        ('vegetables', 'Vegetables'),
        ('fruits', 'Fruits'),
        ('grains', 'Grains & Cereals'),
        ('spices', 'Spices & Condiments'),
        ('beverages', 'Beverages'),
        ('snacks', 'Snacks'),
        ('household', 'Household Items'),
        ('other', 'Other'),
    ]
    
    shopkeeper = models.ForeignKey(Shopkeeper, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.CharField(max_length=50)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')

    def has_orders(self):
        """Check if this product has any orders"""
        # Removed self.order_set as Order no longer has product FK
        return OrderItem.objects.filter(product=self).exists()
    
    def save(self, *args, **kwargs):
        # Check if this is a new product or if price has changed
        if self.pk:
            old_product = Product.objects.get(pk=self.pk)
            if old_product.price != self.price:
                # Price has changed, create a price history entry
                PriceHistory.objects.create(
                    product=self,
                    old_price=old_product.price,
                    new_price=self.price,
                    change_reason='Price updated'
                )
        else:
            # New product, create initial price history entry
            super().save(*args, **kwargs)
            PriceHistory.objects.create(
                product=self,
                old_price=0,
                new_price=self.price,
                change_reason='Initial price'
            )
            return
        
        super().save(*args, **kwargs)

class PriceHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history')
    old_price = models.DecimalField(max_digits=10, decimal_places=2)
    new_price = models.DecimalField(max_digits=10, decimal_places=2)
    change_reason = models.CharField(max_length=100, default='Price updated')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.product.name}: {self.old_price} → {self.new_price} ({self.timestamp})"
    
    @property
    def price_change(self):
        return self.new_price - self.old_price
    
    @property
    def percentage_change(self):
        if self.old_price > 0:
            return ((self.new_price - self.old_price) / self.old_price) * 100
        return 0

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    shopkeeper = models.ForeignKey(Shopkeeper, on_delete=models.CASCADE)
    delivery_partner = models.ForeignKey(DeliveryPartner, on_delete=models.SET_NULL, null=True, blank=True)
    delivery_name = models.CharField(max_length=100, default='Unknown Customer')
    delivery_address = models.CharField(max_length=255)
    delivery_phone = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=50, choices=[
        ('cash_on_delivery', 'Cash on Delivery'),
        ('online_payment', 'Online Payment')
    ], default='cash_on_delivery')
    special_instructions = models.TextField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('ready', 'Ready'),
        ('assigned', 'Assigned'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled')
    ], default='pending')
    date = models.DateTimeField(auto_now_add=True)
    # Removed product foreign key as orders can have multiple products via OrderItem
    # product = models.ForeignKey(Product, on_delete=models.CASCADE)


    def __str__(self):
        return f"Order #{self.id} - {self.customer.name} from {self.shopkeeper.name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=255, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)



    def __str__(self):
        return f"{self.product.name if self.product else '[Deleted Product]'} x{self.quantity} in Order #{self.order.id}"

    @property
    def subtotal(self):
        return self.quantity * self.price


class ProductRequest(models.Model):
    """A customer can request a product from a specific shopkeeper when it is not found."""
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='product_requests')
    shopkeeper = models.ForeignKey(Shopkeeper, on_delete=models.CASCADE, related_name='product_requests')
    product_name = models.CharField(max_length=200)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        status = 'resolved' if self.resolved else 'open'
        return f"{self.product_name} ({status}) for {self.shopkeeper.name} by {self.customer.name}"


class State(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class District(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('state', 'name')

    def __str__(self):
        return f"{self.name}, {self.state.name}"

class Mandal(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('district', 'name')

    def __str__(self):
        return f"{self.name}, {self.district.name}"

class Village(models.Model):
    mandal = models.ForeignKey(Mandal, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('mandal', 'name')

    def __str__(self):
        return f"{self.name}, {self.mandal.name}"
