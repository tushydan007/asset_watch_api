from twilio.rest import Client
from django.conf import settings
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    @staticmethod
    def create_notification(user, title, message, notification_type, **kwargs):
        """Create a notification"""
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            **kwargs,
        )

        # Send real-time notification via WebSocket
        NotificationService.send_realtime_notification(user.id, notification)

        # Send SMS if user has phone number
        if user.phone_number:
            NotificationService.send_sms_notification(notification)

        return notification

    @staticmethod
    def send_realtime_notification(user_id, notification):
        """Send real-time notification via WebSocket"""
        try:
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{user_id}",
                {
                    "type": "notification_message",
                    "notification": {
                        "id": str(notification.id),
                        "title": notification.title,
                        "message": notification.message,
                        "type": notification.notification_type,
                        "created_at": notification.created_at.isoformat(),
                    },
                },
            )
        except Exception as e:
            logger.error(f"Failed to send real-time notification: {e}")

    @staticmethod
    def send_sms_notification(notification):
        """Send SMS notification using Twilio"""
        if not all(
            [
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN,
                settings.TWILIO_PHONE_NUMBER,
            ]
        ):
            logger.warning("Twilio credentials not configured")
            return

        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

            message = client.messages.create(
                body=f"{notification.title}\n\n{notification.message}",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=notification.user.phone_number,
            )

            notification.sms_message_id = message.sid
            notification.sms_status = "sent"
            notification.sms_sent_at = timezone.now()
            notification.save()

        except Exception as e:
            notification.sms_status = "failed"
            notification.save()
            logger.error(f"Failed to send SMS: {e}")

    @staticmethod
    def create_encroachment_notification(encroachment):
        """Create notification for encroachment detection"""
        title = f"Encroachment Detected in {encroachment.aoi.name}"
        message = (
            f"We detected a {encroachment.severity} severity encroachment "
            f"in your AOI '{encroachment.aoi.name}'. "
            f"Confidence: {encroachment.confidence_score:.2f}. "
            f"Please review and take appropriate action."
        )

        return NotificationService.create_notification(
            user=encroachment.aoi.user,
            title=title,
            message=message,
            notification_type="encroachment",
            aoi=encroachment.aoi,
            encroachment=encroachment,
        )

    @staticmethod
    def create_payment_notification(payment, success=True):
        """Create notification for payment events"""
        if success:
            title = "Payment Successful"
            message = (
                f"Your payment of {payment.amount} {payment.currency} "
                f"for {payment.monitoring_type} monitoring has been processed successfully. "
                f"Your AOIs are now being monitored."
            )
        else:
            title = "Payment Failed"
            message = (
                f"Your payment of {payment.amount} {payment.currency} "
                f"could not be processed. Please try again or contact support."
            )

        return NotificationService.create_notification(
            user=payment.user,
            title=title,
            message=message,
            notification_type="payment",
            payment=payment,
        )
