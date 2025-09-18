from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from .models import Cart, CartItem, Order, OrderItem
from aoi.models import Aoi


class CartService:
    """Service for managing cart operations"""

    @staticmethod
    def get_or_create_cart(user):
        """Get or create cart for user"""
        cart, created = Cart.objects.get_or_create(user=user)
        return cart

    @staticmethod
    def add_aoi_to_cart(user, aoi_id, monitoring_type="daily"):
        """Add AOI to user's cart"""
        try:
            aoi = Aoi.objects.get(id=aoi_id, user=user, status="in_cart")
            cart = CartService.get_or_create_cart(user)

            # Check if item already exists in cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                aoi=aoi,
                defaults={
                    "monitoring_type": monitoring_type,
                    "price": CartItem.PRICING.get(
                        monitoring_type, CartItem.PRICING["daily"]
                    ),
                },
            )

            if not created:
                # Update existing item
                cart_item.monitoring_type = monitoring_type
                cart_item.price = CartItem.PRICING.get(
                    monitoring_type, CartItem.PRICING["daily"]
                )
                cart_item.save()

            return cart_item

        except Aoi.DoesNotExist:
            raise ValueError("AOI not found or already paid")

    @staticmethod
    def remove_from_cart(user, cart_item_id):
        """Remove item from cart"""
        cart = CartService.get_or_create_cart(user)
        cart_item = cart.cart_items.get(id=cart_item_id)
        cart_item.delete()

    @staticmethod
    def update_cart_item(user, cart_item_id, monitoring_type):
        """Update cart item monitoring type"""
        cart = CartService.get_or_create_cart(user)
        cart_item = cart.cart_items.get(id=cart_item_id)
        cart_item.monitoring_type = monitoring_type
        cart_item.price = CartItem.PRICING.get(
            monitoring_type, CartItem.PRICING["daily"]
        )
        cart_item.save()
        return cart_item

    @staticmethod
    def clear_cart(user):
        """Clear user's cart"""
        cart = CartService.get_or_create_cart(user)
        cart.cart_items.all().delete()


class OrderService:
    """Service for managing orders"""

    @staticmethod
    @transaction.atomic
    def create_order_from_cart(user, monitoring_type, currency="USD"):
        """Create order from user's cart items"""
        cart = CartService.get_or_create_cart(user)
        cart_items = cart.cart_items.all()

        if not cart_items:
            raise ValueError("Cart is empty")

        # Calculate total amount
        price_per_item = CartItem.PRICING.get(
            monitoring_type, CartItem.PRICING["daily"]
        )
        total_amount = price_per_item * cart_items.count()

        # Create order
        order = Order.objects.create(
            user=user, total_amount=total_amount, currency=currency, status="pending"
        )

        # Create order items from cart items
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                aoi=cart_item.aoi,
                monitoring_type=monitoring_type,
                price=price_per_item,
            )

        return order

    @staticmethod
    @transaction.atomic
    def complete_order(order_id):
        """Complete an order and activate monitoring"""
        try:
            order = Order.objects.get(id=order_id)

            if order.status == "completed":
                return order

            # Mark order as completed
            order.status = "completed"
            order.completed_at = timezone.now()
            order.save()

            # Activate monitoring for all AOIs in the order
            for order_item in order.order_items.all():
                aoi = order_item.aoi
                aoi.monitoring_type = order_item.monitoring_type
                aoi.is_paid = True
                aoi.status = "inactive"  # Will be activated by monitoring system
                aoi.save()

            # Clear user's cart
            CartService.clear_cart(order.user)

            return order

        except Order.DoesNotExist:
            raise ValueError("Order not found")
