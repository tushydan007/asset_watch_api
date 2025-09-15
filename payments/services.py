import stripe
import requests
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
from .models import Payment
from aoi.models import Aoi


class PaymentService:
    # Pricing per AOI in USD
    PRICING = {
        'daily': Decimal('5.00'),
        'monthly': Decimal('100.00'),
        'yearly': Decimal('1000.00'),
    }
    
    @classmethod
    def calculate_amount(cls, aoi_count, monitoring_type):
        """Calculate total payment amount"""
        base_price = cls.PRICING.get(monitoring_type, cls.PRICING['daily'])
        return base_price * aoi_count
    
    @classmethod
    def create_payment(cls, user, aoi_ids, monitoring_type, payment_provider, currency='USD'):
        """Create a new payment record"""
        aois = AOI.objects.filter(id__in=aoi_ids, user=user, is_paid=False)
        
        if not aois.exists():
            raise ValueError("No valid unpaid AOIs found")
        
        amount = cls.calculate_amount(aois.count(), monitoring_type)
        
        payment = Payment.objects.create(
            user=user,
            amount=amount,
            currency=currency,
            monitoring_type=monitoring_type,
            payment_provider=payment_provider
        )
        payment.aois.set(aois)
        
        return payment


class StripePaymentService:
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
    
    def create_payment_intent(self, payment):
        """Create Stripe PaymentIntent"""
        try:
            intent = stripe.PaymentIntent.create(
                amount=payment.amount_cents,
                currency=payment.currency.lower(),
                metadata={
                    'payment_id': str(payment.id),
                    'user_email': payment.user.email,
                    'monitoring_type': payment.monitoring_type,
                }
            )
            
            payment.provider_payment_id = intent.id
            payment.save()
            
            return {
                'client_secret': intent.client_secret,
                'payment_id': str(payment.id)
            }
        except stripe.error.StripeError as e:
            raise ValueError(f"Stripe error: {str(e)}")
    
    def confirm_payment(self, payment_intent_id):
        """Confirm payment and update AOIs"""
        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            payment_id = intent.metadata.get('payment_id')
            
            if intent.status == 'succeeded':
                payment = Payment.objects.get(id=payment_id)
                payment.status = 'completed'
                payment.completed_at = timezone.now()
                payment.save()
                
                # Mark AOIs as paid
                payment.aois.all().update(is_paid=True)
                
                return True
            return False
        except (stripe.error.StripeError, Payment.DoesNotExist):
            return False


class PaystackPaymentService:
    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.base_url = "https://api.paystack.co"
    
    def initialize_payment(self, payment):
        """Initialize Paystack payment"""
        headers = {
            'Authorization': f'Bearer {self.secret_key}',
            'Content-Type': 'application/json'
        }
        
        # Convert amount to kobo (for NGN) or cents
        amount = int(payment.amount * 100)
        
        data = {
            'email': payment.user.email,
            'amount': amount,
            'currency': payment.currency,
            'reference': str(payment.id),
            'callback_url': f'{settings.FRONTEND_URL}/payment/callback',
            'metadata': {
                'payment_id': str(payment.id),
                'monitoring_type': payment.monitoring_type,
                'aoi_count': payment.aois.count()
            }
        }
        
        response = requests.post(
            f'{self.base_url}/transaction/initialize',
            json=data,
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            payment.provider_payment_id = result['data']['reference']
            payment.save()
            
            return {
                'authorization_url': result['data']['authorization_url'],
                'reference': result['data']['reference'],
                'payment_id': str(payment.id)
            }
        else:
            raise ValueError(f"Paystack error: {response.text}")
    
    def verify_payment(self, reference):
        """Verify Paystack payment"""
        headers = {
            'Authorization': f'Bearer {self.secret_key}',
        }
        
        response = requests.get(
            f'{self.base_url}/transaction/verify/{reference}',
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            if result['data']['status'] == 'success':
                payment_id = result['data']['metadata']['payment_id']
                
                try:
                    payment = Payment.objects.get(id=payment_id)
                    payment.status = 'completed'
                    payment.completed_at = timezone.now()
                    payment.save()
                    
                    # Mark AOIs as paid
                    payment.aois.all().update(is_paid=True)
                    
                    return True
                except Payment.DoesNotExist:
                    return False
        return False