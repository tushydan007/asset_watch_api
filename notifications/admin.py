from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "user",
        "notification_type",
        "is_read",
        "sms_status",
        "created_at",
    ]
    list_filter = ["notification_type", "is_read", "sms_status", "created_at"]
    search_fields = ["title", "message", "user__email"]
    readonly_fields = ["id", "created_at", "read_at", "sms_sent_at"]
