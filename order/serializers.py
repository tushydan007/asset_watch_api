from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem
from aoi.serializers import AoiSerializer


class CartItemSerializer(serializers.ModelSerializer):
    aoi = AoiSerializer(read_only=True)
    aoi_id = serializers.UUIDField(write_only=True)
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            "id",
            "aoi",
            "aoi_id",
            "monitoring_type",
            "price",
            "total_price",
            "created_at",
        ]
        read_only_fields = ["id", "price", "created_at"]

    def create(self, validated_data):
        aoi_id = validated_data.pop("aoi_id")
        aoi = AOI.objects.get(id=aoi_id, user=self.context["request"].user)
        validated_data["aoi"] = aoi
        return super().create(validated_data)


class CartSerializer(serializers.ModelSerializer):
    cart_items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Cart
        fields = [
            "id",
            "cart_items",
            "total_items",
            "total_amount",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class OrderItemSerializer(serializers.ModelSerializer):
    aoi = AoiSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "aoi", "monitoring_type", "price"]


class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "order_number",
            "status",
            "total_amount",
            "currency",
            "created_at",
            "updated_at",
            "completed_at",
            "billing_email",
            "billing_first_name",
            "billing_last_name",
            "billing_phone",
            "order_items",
        ]
        read_only_fields = ["id", "order_number", "created_at", "updated_at"]


class OrderCreateSerializer(serializers.Serializer):
    monitoring_type = serializers.ChoiceField(choices=CartItem.MONITORING_TYPE_CHOICES)
    payment_provider = serializers.ChoiceField(
        choices=[("stripe", "Stripe"), ("paystack", "Paystack")]
    )
    currency = serializers.CharField(max_length=3, default="USD")
