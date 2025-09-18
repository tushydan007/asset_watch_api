import django_filters
from .models import Notification


class NotificationFilter(django_filters.FilterSet):
    notification_type = django_filters.ChoiceFilter(
        choices=Notification.NOTIFICATION_TYPE_CHOICES
    )
    is_read = django_filters.BooleanFilter()
    created_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )

    class Meta:
        model = Notification
        fields = ["notification_type", "is_read", "created_after", "created_before"]
