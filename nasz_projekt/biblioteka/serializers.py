from rest_framework import serializers
from .models import Bag, User_acc, Cart, CartItem, OrderSummary, OrderSummaryItem, Order, SIZE, COLOR, FABRIC
import re

ZIP_PL_REGEX = r"^\d{2}-\d{3}$"  


class BagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bag
        fields = "__all__"

    def validate_model(self, value):
        value = str(value).strip()
        if not value:
            raise serializers.ValidationError("Model nie może być pusty.")
        if not value[0].isupper():
            raise serializers.ValidationError("Model musi zaczynać się z dużej litery.")
        return value

    def validate_brand(self, value):
        value = str(value).strip()
        if not value:
            raise serializers.ValidationError("Brand nie może być pusty.")
        if not value[0].isupper():
            raise serializers.ValidationError("Brand musi zaczynać się z dużej litery.")
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Cena musi być większa od zera.")
        return value

    def validate_amount(self, value):
        if value < 0:
            raise serializers.ValidationError("Ilość nie może być mniejsza niż 0.")
        return value


class User_accSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_acc
        exclude = ["django_user"]

    def validate_name(self, value):
        value = str(value).strip()
        if not value:
            raise serializers.ValidationError("Imię nie może być puste.")
        if not value[0].isupper():
            raise serializers.ValidationError("Imię musi zaczynać się z dużej litery.")
        return value

    def validate_surname(self, value):
        value = str(value).strip()
        if not value:
            raise serializers.ValidationError("Nazwisko nie może być puste.")
        if not value[0].isupper():
            raise serializers.ValidationError("Nazwisko musi zaczynać się z dużej litery.")
        return value

    def validate_email(self, value):
        value = str(value).strip()
        return value.lower()

    def validate_zip_code(self, value):
        value = str(value).strip()
        if not re.match(ZIP_PL_REGEX, value):
            raise serializers.ValidationError("Kod pocztowy musi mieć format 12-345.")
        return value

    def validate_phone_number(self, value):
        # PhoneNumberField zwykle już waliduje, ale dorzucamy jasny komunikat:
        if hasattr(value, "is_valid") and not value.is_valid():
            raise serializers.ValidationError("Niepoprawny numer telefonu.")
        return value


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["id", "bag", "quantity", "price_at_time"]
        read_only_fields = ["price_at_time"] 

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Ilość musi być większa od zera.")
        return value
    
    def validate(self, data):
        bag = data.get("bag") or getattr(self.instance, "bag", None)
        quantity = data.get("quantity")

        if bag is not None and quantity is not None:
            if quantity > bag.amount:
                raise serializers.ValidationError(
                    {"quantity": f"Dostępna ilość dla tego produktu to: {bag.amount}."}
                )
        return data
    

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ["id", "user_cart", "created_at", "items", "total_price"]

    def get_total_price(self, obj):
        return sum(
            item.quantity * item.price_at_time
            for item in obj.items.all()
        )


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