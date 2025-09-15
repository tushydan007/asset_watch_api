import requests
import numpy as np
from django.contrib.gis.geos import Polygon, Point
from django.contrib.gis.measure import D
from django.utils import timezone
from datetime import timedelta
from typing import List, Tuple
import logging

from aoi.models import Aoi, EncroachmentDetection
from .models import SatelliteImage

logger = logging.getLogger(__name__)


class SatelliteImageService:
    """Service for managing satellite imagery"""
    
    @staticmethod
    def get_images_for_aoi(aoi: Aoi, start_date=None, end_date=None) -> List[SatelliteImage]:
        """Get satellite images that cover an AOI within date range"""
        queryset = SatelliteImage.objects.filter(
            geometry__intersects=aoi.geometry
        ).order_by('-acquisition_date')
        
        if start_date:
            queryset = queryset.filter(acquisition_date__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(acquisition_date__lte=end_date)
        
        # Filter by cloud coverage (less than 20%)
        queryset = queryset.filter(cloud_coverage__lt=20.0)
        
        return list(queryset[:10])  # Limit to 10 most recent images
    
    @staticmethod
    def fetch_latest_images() -> int:
        """Simulate fetching latest satellite images"""
        # In a real implementation, this would:
        # 1. Connect to satellite data APIs
        # 2. Query for new images
        # 3. Download metadata and thumbnails
        # 4. Store in database
        
        # For demo, we'll create some sample data
        sample_images = [
            {
                'scene_id': f'S2A_MSIL1C_{timezone.now().strftime("%Y%m%dT%H%M%S")}',
                'satellite': 'Sentinel-2',
                'acquisition_date': timezone.now() - timedelta(hours=6),
                'cloud_coverage': 5.2,
                'geometry': Polygon.from_bbox((3.0, 6.0, 4.0, 7.0)),  # Lagos area
                'image_url': 'https://example.com/satellite/image1.tif',
                'thumbnail_url': 'https://example.com/satellite/thumb1.jpg',
            }
        ]
        
        created_count = 0
        for img_data in sample_images:
            image, created = SatelliteImage.objects.get_or_create(
                scene_id=img_data['scene_id'],
                defaults=img_data
            )
            if created:
                created_count += 1
        
        return created_count


class EncroachmentDetectionService:
    """Service for detecting encroachments using AI/ML"""
    
    @staticmethod
    def detect_encroachment(aoi: Aoi, satellite_image: SatelliteImage) -> List[EncroachmentDetection]:
        """Detect encroachments in AOI using satellite imagery"""
        try:
            # In a real implementation, this would:
            # 1. Download the satellite image
            # 2. Crop to AOI bounds
            # 3. Run AI model for change detection
            # 4. Analyze results for encroachments
            
            # For demo purposes, we'll simulate detection
            encroachments = []
            
            # Simulate random encroachment detection (10% chance)
            if np.random.random() < 0.1:
                # Create a simulated encroachment within the AOI
                aoi_bounds = aoi.geometry.extent  # (xmin, ymin, xmax, ymax)
                
                # Create a small polygon within the AOI bounds
                center_x = (aoi_bounds[0] + aoi_bounds[2]) / 2
                center_y = (aoi_bounds[1] + aoi_bounds[3]) / 2
                
                # Create a small rectangle around the center
                offset = 0.001  # Small offset for demo
                affected_area = Polygon.from_bbox((
                    center_x - offset,
                    center_y - offset,
                    center_x + offset,
                    center_y + offset
                ))
                
                # Determine severity based on simulated analysis
                severities = ['low', 'medium', 'high', 'critical']
                severity = np.random.choice(severities, p=[0.4, 0.3, 0.2, 0.1])
                
                confidence_score = np.random.uniform(0.7, 0.95)
                
                encroachment = EncroachmentDetection.objects.create(
                    aoi=aoi,
                    severity=severity,
                    affected_area=affected_area,
                    confidence_score=confidence_score,
                    description=f"Potential {severity} encroachment detected through satellite analysis. "
                               f"Change detected in vegetation/land use pattern.",
                    satellite_image_url=satellite_image.image_url
                )
                
                encroachments.append(encroachment)
                
                logger.info(
                    f"Detected {severity} encroachment in AOI {aoi.name} "
                    f"with confidence {confidence_score:.2f}"
                )
            
            return encroachments
            
        except Exception as e:
            logger.error(f"Error detecting encroachment for AOI {aoi.name}: {e}")
            return []
    
    @staticmethod
    def analyze_image_with_ai(image_url: str, aoi_geometry: Polygon) -> dict:
        """Analyze satellite image using AI/ML models"""
        # In a real implementation, this would:
        # 1. Load pre-trained models (e.g., using TensorFlow/PyTorch)
        # 2. Preprocess the satellite image
        # 3. Run inference for change detection
        # 4. Post-process results
        
        # For demo, return simulated results
        return {
            'change_detected': np.random.random() > 0.8,
            'confidence': np.random.uniform(0.6, 0.95),
            'change_type': np.random.choice(['deforestation', 'construction', 'mining', 'agriculture']),
            'affected_area_percentage': np.random.uniform(0.1, 5.0)
        }