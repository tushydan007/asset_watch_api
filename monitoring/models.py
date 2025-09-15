from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class SatelliteImage(models.Model):
    """Model to store satellite imagery metadata"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scene_id = models.CharField(max_length=255, unique=True)
    satellite = models.CharField(max_length=50)  # e.g., 'Sentinel-2', 'Landsat-8'
    acquisition_date = models.DateTimeField()
    cloud_coverage = models.FloatField()
    geometry = models.PolygonField(srid=4326)  # Scene footprint
    image_url = models.URLField()
    thumbnail_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'satellite_image'
        ordering = ['-acquisition_date']
    
    def __str__(self):
        return f"{self.satellite} - {self.scene_id}"


class MonitoringJob(models.Model):
    """Track monitoring jobs for AOIs"""
    JOB_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    aoi = models.ForeignKey('aoi.AOI', on_delete=models.CASCADE, related_name='monitoring_jobs')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=JOB_STATUS_CHOICES, default='pending')
    celery_task_id = models.CharField(max_length=255, blank=True)
    error_message = models.TextField(blank=True)
    images_processed = models.IntegerField(default=0)
    encroachments_detected = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'monitoring_job'
        ordering = ['-started_at']
    
    def __str__(self):
        return f"Monitoring Job {self.id} - {self.aoi.name}"