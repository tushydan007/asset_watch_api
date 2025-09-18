from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from .models import MonitoringJob, SatelliteImage


@admin.register(MonitoringJob)
class MonitoringJobAdmin(GISModelAdmin):
    list_display = [
        "id",
        "aoi",
        "status",
        "started_at",
        "completed_at",
        "images_processed",
        "encroachments_detected",
    ]
    list_filter = ["status", "started_at"]
    search_fields = ["aoi__name", "aoi__user__email"]
    readonly_fields = ["id", "started_at", "completed_at", "celery_task_id"]


@admin.register(SatelliteImage)
class SatelliteImageAdmin(GISModelAdmin):
    list_display = ["scene_id", "satellite", "acquisition_date", "cloud_coverage"]
    list_filter = ["satellite", "acquisition_date"]
    search_fields = ["scene_id"]
