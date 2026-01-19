from rest_framework import serializers
from .models import Bag, User_acc, Cart, CartItem, OrderSummary, OrderSummaryItem, Order, SIZE, COLOR, FABRIC

class BagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bag
        fields = "__all__"
    

class User_accSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_acc
        exclude = ["django_user"]

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = "__all__"

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer( many = True, read_only = True)
    class Meta:
        model = Cart
        fields = "__all__"


class OrderSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderSummary
        fields = "__all__"

class OrderSummaryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderSummaryItem
        fields = "__all__"

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"