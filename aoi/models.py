from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
import uuid

User = get_user_model()


class Aoi(models.Model):
    MONITORING_CHOICES = [
        ('daily', 'Daily'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('expired', 'Expired'),
        ('in_cart', 'In Cart'),  # Added for cart functionality
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='aois')
    name = models.CharField(max_length=255)
    geometry = models.PolygonField(srid=4326)
    monitoring_type = models.CharField(max_length=10, choices=MONITORING_CHOICES, default='daily')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='in_cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    is_paid = models.BooleanField(default=False)
    
    # Cart-specific fields
    added_to_cart_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'aoi'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.user.email}"
    
    def activate_monitoring(self):
        """Activate monitoring and set dates based on monitoring type"""
        self.status = 'active'
        self.start_date = timezone.now()
        
        if self.monitoring_type == 'daily':
            self.end_date = self.start_date + timezone.timedelta(days=1)
        elif self.monitoring_type == 'monthly':
            self.end_date = self.start_date + timezone.timedelta(days=30)
        elif self.monitoring_type == 'yearly':
            self.end_date = self.start_date + timezone.timedelta(days=365)
        
        self.save()


class EncroachmentDetection(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    aoi = models.ForeignKey(Aoi, on_delete=models.CASCADE, related_name='encroachments')
    detected_at = models.DateTimeField(auto_now_add=True)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    affected_area = models.PolygonField(srid=4326)
    confidence_score = models.FloatField()
    description = models.TextField()
    satellite_image_url = models.URLField(blank=True)
    is_confirmed = models.BooleanField(default=False)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'encroachment_detection'
        ordering = ['-detected_at']
    
    def __str__(self):
        return f"Encroachment in {self.aoi.name} - {self.severity}"