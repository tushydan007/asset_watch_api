import django_filters
from .models import Aoi, EncroachmentDetection


class AoiFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=Aoi.STATUS_CHOICES)
    monitoring_type = django_filters.ChoiceFilter(choices=Aoi.MONITORING_CHOICES)
    is_paid = django_filters.BooleanFilter()
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Aoi
        fields = ['status', 'monitoring_type', 'is_paid']


class EncroachmentDetectionFilter(django_filters.FilterSet):
    severity = django_filters.ChoiceFilter(choices=EncroachmentDetection.SEVERITY_CHOICES)
    is_confirmed = django_filters.BooleanFilter()
    detected_after = django_filters.DateTimeFilter(field_name='detected_at', lookup_expr='gte')
    detected_before = django_filters.DateTimeFilter(field_name='detected_at', lookup_expr='lte')
    aoi = django_filters.UUIDFilter()
    
    class Meta:
        model = EncroachmentDetection
        fields = ['severity', 'is_confirmed', 'aoi']