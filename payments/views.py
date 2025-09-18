from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse
import stripe
import json
from .models import Payment, PaymentWebhook
from .serializers import PaymentCreateSerializer, PaymentSerializer
from .services import PaymentService, StripePaymentService, PaystackPaymentService
from order.models import Order


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)
    
    def create(self, request):
        """Create a new payment"""
        serializer = PaymentCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                order_id = serializer.validated_data['order_id']
                payment_provider = serializer.validated_data['payment_provider']
                
                # Get the order
                order = Order.objects.get(id=order_id, user=request.user, status='pending')
                
                # Create payment
                payment = PaymentService.create_payment(
                    user=request.user,
                    order=order,
                    payment_provider=payment_provider
                )
                
                # Initialize payment with chosen provider
                if payment.payment_provider == 'stripe':
                    stripe_service = StripePaymentService()
                    result = stripe_service.create_payment_intent(payment)
                elif payment.payment_provider == 'paystack':
                    paystack_service = PaystackPaymentService()
                    result = paystack_service.initialize_payment(payment)
                
                return Response({
                    'payment': PaymentSerializer(payment).data,
                    **result
                }, status=status.HTTP_201_CREATED)
                
            except (ValueError, Order.DoesNotExist) as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def pricing(self, request):
        """Get pricing information"""
        from order.models import CartItem
        return Response(CartItem.PRICING)
    
    @action(detail=True, methods=['post'])
    def verify_paystack(self, request, pk=None):
        """Verify Paystack payment"""
        payment = self.get_object()
        if payment.payment_provider != 'paystack':
            return Response(
                {'error': 'Invalid payment provider'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        paystack_service = PaystackPaymentService()
        success = paystack_service.verify_payment(payment.provider_payment_id)
        
        if success:
            return Response({'status': 'success'})
        else:
            return Response(
                {'error': 'Payment verification failed'},
                status=status.HTTP_400_BAD_REQUEST
            )


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhooks"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    # Store webhook for processing
    webhook, created = PaymentWebhook.objects.get_or_create(
        provider='stripe',
        webhook_id=event['id'],
        defaults={
            'event_type': event['type'],
            'data': event['data']
        }
    )
    
    if not created:
        return HttpResponse(status=200)
    
    # Process the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        stripe_service = StripePaymentService()
        stripe_service.confirm_payment(payment_intent['id'])
        webhook.processed = True
        webhook.save()
    
    return HttpResponse(status=200)


@csrf_exempt
@require_POST
def paystack_webhook(request):
    """Handle Paystack webhooks"""
    payload = request.body
    
    try:
        event = json.loads(payload)
    except json.JSONDecodeError:
        return HttpResponse(status=400)
    
    # Store webhook for processing
    webhook, created = PaymentWebhook.objects.get_or_create(
        provider='paystack',
        webhook_id=event.get('id', ''),
        defaults={
            'event_type': event.get('event'),
            'data': event.get('data', {})
        }
    )
    
    if not created:
        return HttpResponse(status=200)
    
    # Process the event
    if event.get('event') == 'charge.success':
        reference = event['data'].get('reference')
        if reference:
            paystack_service = PaystackPaymentService()
            paystack_service.verify_payment(reference)
            webhook.processed = True
            webhook.save()
    
    return HttpResponse(status=200)
