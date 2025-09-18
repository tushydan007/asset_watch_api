from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"payments", views.PaymentViewSet, basename="payment")

urlpatterns = [
    path("api/", include(router.urls)),
    path("webhooks/stripe/", views.stripe_webhook, name="stripe_webhook"),
    path("webhooks/paystack/", views.paystack_webhook, name="paystack_webhook"),
]
