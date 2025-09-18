from rest_framework import serializers
from .models import Payment


class PaymentCreateSerializer(serializers.ModelSerializer):
    order_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Payment
        fields = ['payment_provider', 'order_id']


class PaymentSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'order_number', 'amount', 'currency', 'monitoring_type',
            'payment_provider', 'status', 'created_at', 'updated_at', 'completed_at'
        ]
