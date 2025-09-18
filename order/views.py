from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Cart, CartItem, Order, OrderItem
from .serializers import (
    CartSerializer,
    CartItemSerializer,
    OrderSerializer,
    OrderCreateSerializer,
)
from .services import CartService, OrderService
from aoi.models import Aoi
from aoi.serializers import AoiSerializer


class CartViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user's cart"""

    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def list(self, request):
        """Get user's cart"""
        cart = CartService.get_or_create_cart(request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def add_item(self, request):
        """Add AOI to cart"""
        aoi_id = request.data.get("aoi_id")
        monitoring_type = request.data.get("monitoring_type", "daily")

        if not aoi_id:
            return Response(
                {"error": "aoi_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            cart_item = CartService.add_aoi_to_cart(
                request.user, aoi_id, monitoring_type
            )
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except (ValueError, Aoi.DoesNotExist) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"])
    def remove_item(self, request):
        """Remove item from cart"""
        cart_item_id = request.data.get("cart_item_id")

        if not cart_item_id:
            return Response(
                {"error": "cart_item_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            CartService.remove_from_cart(request.user, cart_item_id)
            return Response({"message": "Item removed from cart"})

        except CartItem.DoesNotExist:
            return Response(
                {"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=["post"])
    def update_item(self, request):
        """Update cart item"""
        cart_item_id = request.data.get("cart_item_id")
        monitoring_type = request.data.get("monitoring_type")

        if not cart_item_id or not monitoring_type:
            return Response(
                {"error": "cart_item_id and monitoring_type are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            cart_item = CartService.update_cart_item(
                request.user, cart_item_id, monitoring_type
            )
            serializer = CartItemSerializer(cart_item)
            return Response(serializer.data)

        except CartItem.DoesNotExist:
            return Response(
                {"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=["post"])
    def clear(self, request):
        """Clear cart"""
        CartService.clear_cart(request.user)
        return Response({"message": "Cart cleared"})

    @action(detail=False, methods=["get"])
    def count(self, request):
        """Get cart item count"""
        cart = CartService.get_or_create_cart(request.user)
        return Response({"count": cart.total_items})


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet for managing orders"""

    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status"]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def create(self, request):
        """Create order from cart"""
        serializer = OrderCreateSerializer(data=request.data)

        if serializer.is_valid():
            try:
                order = OrderService.create_order_from_cart(
                    user=request.user,
                    monitoring_type=serializer.validated_data["monitoring_type"],
                    currency=serializer.validated_data.get("currency", "USD"),
                )

                order_serializer = OrderSerializer(order)
                return Response(order_serializer.data, status=status.HTTP_201_CREATED)

            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
