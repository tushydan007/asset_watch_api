from celery import shared_task
from django.utils import timezone
from django.contrib.gis.geos import Polygon
from django.contrib.gis.db.models import Q
import requests
import numpy as np
from datetime import timedelta
import logging

from aoi.models import Aoi, EncroachmentDetection
from notifications.services import NotificationService
from .models import MonitoringJob, SatelliteImage
from .services import EncroachmentDetectionService, SatelliteImageService

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def monitor_aoi_task(self, aoi_id):
    """Monitor a single AOI for encroachments"""
    try:
        aoi = Aoi.objects.get(id=aoi_id, status='active')
        
        # Create monitoring job
        job = MonitoringJob.objects.create(
            aoi=aoi,
            status='running',
            celery_task_id=self.request.id
        )
        
        logger.info(f"Starting monitoring for AOI {aoi.name}")
        
        # Get recent satellite images covering the AOI
        images = SatelliteImageService.get_images_for_aoi(
            aoi,
            start_date=timezone.now() - timedelta(days=7)
        )
        
        encroachments_found = 0
        images_processed = 0
        
        for image in images:
            try:
                # Process image for encroachment detection
                encroachments = EncroachmentDetectionService.detect_encroachment(
                    aoi, image
                )
                
                encroachments_found += len(encroachments)
                images_processed += 1
                
                # Create notifications for detected encroachments
                for encroachment in encroachments:
                    NotificationService.create_encroachment_notification(encroachment)
                
            except Exception as e:
                logger.error(f"Error processing image {image.scene_id}: {e}")
                continue
        
        # Update job status
        job.status = 'completed'
        job.completed_at = timezone.now()
        job.images_processed = images_processed
        job.encroachments_detected = encroachments_found
        job.save()
        
        logger.info(
            f"Completed monitoring for AOI {aoi.name}. "
            f"Processed {images_processed} images, found {encroachments_found} encroachments"
        )
        
        return {
            'aoi_id': str(aoi.id),
            'images_processed': images_processed,
            'encroachments_detected': encroachments_found
        }
        
    except AOI.DoesNotExist:
        logger.error(f"AOI {aoi_id} not found or not active")
        return {'error': 'AOI not found or not active'}
    
    except Exception as e:
        logger.error(f"Error monitoring AOI {aoi_id}: {e}")
        
        # Update job status on failure
        try:
            job.status = 'failed'
            job.error_message = str(e)
            job.completed_at = timezone.now()
            job.save()
        except:
            pass
        
        raise


@shared_task
def schedule_monitoring_jobs():
    """Schedule monitoring jobs for active AOIs"""
    active_aois = Aoi.objects.filter(
        status='active',
        is_paid=True,
        end_date__gt=timezone.now()
    )
    
    jobs_scheduled = 0
    
    for aoi in active_aois:
        # Check if we should run monitoring based on monitoring type
        should_monitor = False
        last_job = aoi.monitoring_jobs.filter(
            status='completed'
        ).order_by('-completed_at').first()
        
        now = timezone.now()
        
        if not last_job:
            should_monitor = True
        elif aoi.monitoring_type == 'daily':
            should_monitor = last_job.completed_at < now - timedelta(hours=23)
        elif aoi.monitoring_type == 'monthly':
            should_monitor = last_job.completed_at < now - timedelta(days=29)
        elif aoi.monitoring_type == 'yearly':
            should_monitor = last_job.completed_at < now - timedelta(days=364)
        
        if should_monitor:
            # Check if there's already a pending/running job
            existing_job = aoi.monitoring_jobs.filter(
                status__in=['pending', 'running']
            ).exists()
            
            if not existing_job:
                monitor_aoi_task.delay(str(aoi.id))
                jobs_scheduled += 1
    
    logger.info(f"Scheduled {jobs_scheduled} monitoring jobs")
    return {'jobs_scheduled': jobs_scheduled}


@shared_task
def fetch_satellite_images():
    """Fetch new satellite images from various sources"""
    try:
        images_fetched = SatelliteImageService.fetch_latest_images()
        logger.info(f"Fetched {images_fetched} new satellite images")
        return {'images_fetched': images_fetched}
        
    except Exception as e:
        logger.error(f"Error fetching satellite images: {e}")
        raise


@shared_task
def cleanup_old_data():
    """Clean up old monitoring jobs and notifications"""
    try:
        from notifications.models import Notification
        
        cutoff_date = timezone.now() - timedelta(days=90)
        
        # Clean up old monitoring jobs
        old_jobs = MonitoringJob.objects.filter(
            completed_at__lt=cutoff_date
        )
        jobs_deleted = old_jobs.count()
        old_jobs.delete()
        
        # Clean up old notifications (keep for 30 days)
        notification_cutoff = timezone.now() - timedelta(days=30)
        old_notifications = Notification.objects.filter(
            created_at__lt=notification_cutoff
        )
        notifications_deleted = old_notifications.count()
        old_notifications.delete()
        
        logger.info(
            f"Cleanup completed: {jobs_deleted} jobs, {notifications_deleted} notifications deleted"
        )
        
        return {
            'jobs_deleted': jobs_deleted,
            'notifications_deleted': notifications_deleted
        }
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        raise
