from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    aoi_name = serializers.CharField(source="aoi.name", read_only=True)

    class Meta:
        model = Notification
        fields = [
            "id",
            "title",
            "message",
            "notification_type",
            "is_read",
            "created_at",
            "read_at",
            "sms_status",
            "aoi_name",
        ]
        read_only_fields = ["id", "created_at", "read_at", "sms_status"]
