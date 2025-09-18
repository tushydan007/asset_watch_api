from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["user", "total_items", "created_at"]
    search_fields = ["user__email"]
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ["cart", "aoi", "monitoring_type", "price", "created_at"]
    list_filter = ["monitoring_type", "created_at"]
    search_fields = ["cart__user__email", "aoi__name"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_number", "user", "status", "total_amount", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["order_number", "user__email"]
    readonly_fields = ["id", "order_number", "created_at", "updated_at"]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ["order", "aoi", "monitoring_type", "price"]
    search_fields = ["order__order_number", "aoi__name"]
