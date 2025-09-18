from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
import uuid

User = get_user_model()


class Cart(models.Model):
    """User's shopping cart for AOIs"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cart'
    
    def __str__(self):
        return f"Cart for {self.user.email}"
    
    @property
    def total_items(self):
        return self.cart_items.count()
    
    @property
    def total_amount(self):
        return sum(item.total_price for item in self.cart_items.all())


class CartItem(models.Model):
    """Individual items in a cart"""
    MONITORING_TYPE_CHOICES = [
        ('daily', 'Daily'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    # Pricing configuration
    PRICING = {
        'daily': Decimal('5.00'),
        'monthly': Decimal('100.00'),
        'yearly': Decimal('1000.00'),
    }
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    aoi = models.ForeignKey('aoi.Aoi', on_delete=models.CASCADE, related_name='cart_items')
    monitoring_type = models.CharField(max_length=10, choices=MONITORING_TYPE_CHOICES, default='daily')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cart_item'
        unique_together = ['cart', 'aoi']
    
    def __str__(self):
        return f"{self.aoi.name} - {self.monitoring_type} monitoring"
    
    def save(self, *args, **kwargs):
        # Set price based on monitoring type
        if not self.price:
            self.price = self.PRICING.get(self.monitoring_type, self.PRICING['daily'])
        super().save(*args, **kwargs)
    
    @property
    def total_price(self):
        return self.price


class Order(models.Model):
    """Order containing multiple AOIs for monitoring"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Billing information
    billing_email = models.EmailField()
    billing_first_name = models.CharField(max_length=50)
    billing_last_name = models.CharField(max_length=50)
    billing_phone = models.CharField(max_length=20, blank=True)
    
    class Meta:
        db_table = 'order'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_number} - {self.user.email}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number
            import time
            timestamp = str(int(time.time()))[-8:]
            self.order_number = f"AOI{timestamp}"
        
        if not self.billing_email:
            self.billing_email = self.user.email
            self.billing_first_name = self.user.first_name
            self.billing_last_name = self.user.last_name
        
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    """Individual AOI items in an order"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    aoi = models.ForeignKey('aoi.Aoi', on_delete=models.CASCADE, related_name='order_items')
    monitoring_type = models.CharField(max_length=10)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'order_item'
        unique_together = ['order', 'aoi']
    
    def __str__(self):
        return f"{self.aoi.name} in Order {self.order.order_number}"