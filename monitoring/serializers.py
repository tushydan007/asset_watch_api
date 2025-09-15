from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import MonitoringJob, SatelliteImage


class MonitoringJobSerializer(serializers.ModelSerializer):
    aoi_name = serializers.CharField(source='aoi.name', read_only=True)
    
    class Meta:
        model = MonitoringJob
        fields = [
            'id', 'aoi', 'aoi_name', 'started_at', 'completed_at',
            'status', 'error_message', 'images_processed', 'encroachments_detected'
        ]


class SatelliteImageSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = SatelliteImage
        geo_field = 'geometry'
        fields = [
            'id', 'scene_id', 'satellite', 'acquisition_date',
            'cloud_coverage', 'geometry', 'image_url', 'thumbnail_url'
        ]