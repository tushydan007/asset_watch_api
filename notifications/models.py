from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ("encroachment", "Encroachment Detection"),
        ("payment", "Payment"),
        ("system", "System"),
        ("monitoring", "Monitoring"),
    ]

    DELIVERY_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("sent", "Sent"),
        ("delivered", "Delivered"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPE_CHOICES
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    # SMS notification fields
    sms_status = models.CharField(
        max_length=20, choices=DELIVERY_STATUS_CHOICES, default="pending"
    )
    sms_sent_at = models.DateTimeField(null=True, blank=True)
    sms_message_id = models.CharField(max_length=255, blank=True)

    # Related objects
    aoi = models.ForeignKey("aoi.AOI", on_delete=models.CASCADE, null=True, blank=True)
    encroachment = models.ForeignKey(
        "aoi.EncroachmentDetection", on_delete=models.CASCADE, null=True, blank=True
    )
    payment = models.ForeignKey(
        "payments.Payment", on_delete=models.CASCADE, null=True, blank=True
    )

    class Meta:
        db_table = "notification"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.user.email}"
