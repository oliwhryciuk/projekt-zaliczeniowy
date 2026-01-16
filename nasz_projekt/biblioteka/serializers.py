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


class CartSerializers(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = "__all__"


class CartItemSerializers(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = "__all__"

class OrderSummarySerializers(serializers.ModelSerializer):
    class Meta:
        model = OrderSummary
        fields = "__all__"

class OrderSummaryItemSerializers(serializers.ModelSerializer):
    class Meta:
        model = OrderSummaryItem
        fields = "__all__"

class OrderSerializers(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"