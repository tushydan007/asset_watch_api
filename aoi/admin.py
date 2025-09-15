from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin
from .models import Aoi, EncroachmentDetection


@admin.register(Aoi)
class AoiAdmin(GISModelAdmin):
    list_display = ['name', 'user', 'monitoring_type', 'status', 'is_paid', 'created_at']
    list_filter = ['monitoring_type', 'status', 'is_paid', 'created_at']
    search_fields = ['name', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at']
    

@admin.register(EncroachmentDetection)
class EncroachmentDetectionAdmin(GISModelAdmin):
    list_display = ['aoi', 'severity', 'confidence_score', 'is_confirmed', 'detected_at']
    list_filter = ['severity', 'is_confirmed', 'detected_at']
    search_fields = ['aoi__name', 'aoi__user__email']
    readonly_fields = ['id', 'detected_at', 'confirmed_at']