from django.contrib import admin
from .models import Payment, PaymentWebhook


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "user",
        "amount",
        "currency",
        "monitoring_type",
        "payment_provider",
        "status",
        "created_at",
    ]
    list_filter = ["status", "payment_provider", "monitoring_type", "created_at"]
    search_fields = ["user__email", "provider_payment_id"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(PaymentWebhook)
class PaymentWebhookAdmin(admin.ModelAdmin):
    list_display = ["id", "provider", "event_type", "processed", "created_at"]
    list_filter = ["provider", "event_type", "processed", "created_at"]
    readonly_fields = ["id", "created_at"]
