from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_PROVIDER_CHOICES = [
        ('stripe', 'Stripe'),
        ('paystack', 'Paystack'),
    ]
    
    MONITORING_TYPE_CHOICES = [
        ('daily', 'Daily'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    aois = models.ManyToManyField('aoi.AOI', related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    monitoring_type = models.CharField(max_length=10, choices=MONITORING_TYPE_CHOICES)
    payment_provider = models.CharField(max_length=10, choices=PAYMENT_PROVIDER_CHOICES)
    provider_payment_id = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'payment'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment {self.id} - {self.user.email} - {self.amount} {self.currency}"
    
    @property
    def amount_cents(self):
        """Return amount in cents for Stripe"""
        return int(self.amount * 100)


class PaymentWebhook(models.Model):
    WEBHOOK_PROVIDER_CHOICES = [
        ('stripe', 'Stripe'),
        ('paystack', 'Paystack'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.CharField(max_length=10, choices=WEBHOOK_PROVIDER_CHOICES)
    webhook_id = models.CharField(max_length=255)
    event_type = models.CharField(max_length=100)
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()
    
    class Meta:
        db_table = 'payment_webhook'
        unique_together = ['provider', 'webhook_id']