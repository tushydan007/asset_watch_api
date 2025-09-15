from rest_framework import serializers
from .models import Payment
from aoi.serializers import AoiSerializer


class PaymentCreateSerializer(serializers.ModelSerializer):
    aoi_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True
    )
    
    class Meta:
        model = Payment
        fields = ['monitoring_type', 'payment_provider', 'currency', 'aoi_ids']
    
    def validate_aoi_ids(self, value):
        if not value:
            raise serializers.ValidationError("At least one AOI must be selected")
        return value


class PaymentSerializer(serializers.ModelSerializer):
    aois = AoiSerializer(many=True, read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'aois', 'amount', 'currency', 'monitoring_type',
            'payment_provider', 'status', 'created_at', 'updated_at', 'completed_at'
        ]