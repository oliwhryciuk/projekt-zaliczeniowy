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
            raise serializers.ValidationError("Model cannot be empty.")
        if not value[0].isupper():
            raise serializers.ValidationError("Model must start with an uppercase letter.")
        return value

    def validate_brand(self, value):
        value = str(value).strip()
        if not value:
            raise serializers.ValidationError("Brand cannot be empty.")
        if not value[0].isupper():
            raise serializers.ValidationError("Brand must start with an uppercase letter.")
        return value

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than zero.")
        return value

    def validate_amount(self, value):
        if value < 0:
            raise serializers.ValidationError("Amount cannot be less than 0.")
        return value


class User_accSerializer(serializers.ModelSerializer):
    class Meta:
        model = User_acc
        exclude = ["django_user"]

    def validate_name(self, value):
        value = str(value).strip()
        if not value:
            raise serializers.ValidationError("First name cannot be empty.")
        if not value[0].isupper():
            raise serializers.ValidationError("First name must start with an uppercase letter.")
        return value

    def validate_surname(self, value):
        value = str(value).strip()
        if not value:
            raise serializers.ValidationError("Last name cannot be empty.")
        if not value[0].isupper():
            raise serializers.ValidationError("Last name must start with an uppercase letter.")
        return value

    def validate_email(self, value):
        value = str(value).strip()
        return value.lower()

    def validate_zip_code(self, value):
        value = str(value).strip()
        if not re.match(ZIP_PL_REGEX, value):
            raise serializers.ValidationError("Zip code must be in format 12-345.")
        return value

    def validate_phone_number(self, value):
        # PhoneNumberField usually validates already, but we add a clear message:
        if hasattr(value, "is_valid") and not value.is_valid():
            raise serializers.ValidationError("Invalid phone number.")
        return value


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["id", "bag", "quantity", "price_at_time"]
        read_only_fields = ["price_at_time"] 

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return value
    
    def validate(self, data):
        bag = data.get("bag") or getattr(self.instance, "bag", None)
        quantity = data.get("quantity")

        if bag is not None and quantity is not None:
            if quantity > bag.amount:
                raise serializers.ValidationError(
                    {"quantity": f"Available quantity for this product is: {bag.amount}."}
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


class CheckoutSerializer(serializers.Serializer):
    """Serializer for checkout form validation"""
    name = serializers.CharField(
        max_length=100,
        required=True,
        error_messages={
            'blank': 'First name cannot be empty.',
            'max_length': 'First name cannot exceed 100 characters.',
            'required': 'First name is required.'
        }
    )
    surname = serializers.CharField(
        max_length=100,
        required=True,
        error_messages={
            'blank': 'Last name cannot be empty.',
            'max_length': 'Last name cannot exceed 100 characters.',
            'required': 'Last name is required.'
        }
    )
    email = serializers.EmailField(
        required=True,
        error_messages={
            'blank': 'Email cannot be empty.',
            'invalid': 'Please enter a valid email address.',
            'required': 'Email is required.'
        }
    )
    street_name = serializers.CharField(
        max_length=100,
        required=True,
        error_messages={
            'blank': 'Street name cannot be empty.',
            'max_length': 'Street name cannot exceed 100 characters.',
            'required': 'Street name is required.'
        }
    )
    home_nr = serializers.CharField(
        max_length=10,
        required=True,
        error_messages={
            'blank': 'House number cannot be empty.',
            'max_length': 'House number cannot exceed 10 characters.',
            'required': 'House number is required.'
        }
    )
    city = serializers.CharField(
        max_length=100,
        required=True,
        error_messages={
            'blank': 'City cannot be empty.',
            'max_length': 'City cannot exceed 100 characters.',
            'required': 'City is required.'
        }
    )
    zip_code = serializers.CharField(
        max_length=10,
        required=True,
        error_messages={
            'blank': 'Zip code cannot be empty.',
            'max_length': 'Zip code cannot exceed 10 characters.',
            'required': 'Zip code is required.'
        }
    )
    country = serializers.CharField(
        max_length=100,
        required=True,
        error_messages={
            'blank': 'Country cannot be empty.',
            'max_length': 'Country cannot exceed 100 characters.',
            'required': 'Country is required.'
        }
    )
    phone_number = serializers.CharField(
        max_length=20,
        required=True,
        error_messages={
            'blank': 'Phone number cannot be empty.',
            'max_length': 'Phone number cannot exceed 20 characters.',
            'required': 'Phone number is required.'
        }
    )

    def validate_name(self, value):
        """Validate that first name starts with a capital letter and contains only letters and spaces"""
        value = str(value).strip()
        if not value:
            raise serializers.ValidationError("First name cannot be empty.")
        if not value[0].isupper():
            raise serializers.ValidationError("First name must start with a capital letter.")
        if not re.match(r"^[A-Z][a-zA-Z\s'-]*$", value):
            raise serializers.ValidationError("First name can only contain letters, spaces, hyphens, and apostrophes.")
        return value

    def validate_surname(self, value):
        """Validate that last name starts with a capital letter and contains only letters and spaces"""
        value = str(value).strip()
        if not value:
            raise serializers.ValidationError("Last name cannot be empty.")
        if not value[0].isupper():
            raise serializers.ValidationError("Last name must start with a capital letter.")
        if not re.match(r"^[A-Z][a-zA-Z\s'-]*$", value):
            raise serializers.ValidationError("Last name can only contain letters, spaces, hyphens, and apostrophes.")
        return value

    def validate_email(self, value):
        """Validate and normalize email address"""
        value = str(value).strip().lower()
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, value):
            raise serializers.ValidationError("Please enter a valid email address.")
        return value

    def validate_phone_number(self, value):
        """Validate phone number (at least 9 digits, may contain spaces, dashes, parentheses)"""
        # Remove common formatting characters
        cleaned = re.sub(r'[\s\-+().]', '', str(value))
        if not cleaned.isdigit():
            raise serializers.ValidationError("Phone number can only contain digits and formatting characters (spaces, dashes, parentheses).")
        if len(cleaned) < 9:
            raise serializers.ValidationError("Phone number must contain at least 9 digits.")
        if len(cleaned) > 15:
            raise serializers.ValidationError("Phone number cannot exceed 15 digits.")
        return value

    def validate_zip_code(self, value):
        """Validate zip code format (supports Polish XX-XXX, XXXXX, or other common formats)"""
        value = str(value).strip()
        if not re.match(r'^[0-9]{2}-?[0-9]{3}$|^[0-9]{5}$|^[A-Z0-9\s-]{3,10}$', value):
            raise serializers.ValidationError("Please enter a valid zip code (e.g., 12-345 or 12345).")
        return value

    def validate_street_name(self, value):
        """Validate that street name is not empty"""
        value = str(value).strip()
        if not value:
            raise serializers.ValidationError("Street name cannot be empty.")
        return value

    def validate_home_nr(self, value):
        """Validate that house number is not empty"""
        value = str(value).strip()
        if not value:
            raise serializers.ValidationError("House number cannot be empty.")
        return value

    def validate_city(self, value):
        """Validate that city is not empty"""
        value = str(value).strip()
        if not value:
            raise serializers.ValidationError("City cannot be empty.")
        return value

    def validate_country(self, value):
        """Validate that country is not empty"""
        value = str(value).strip()
        if not value:
            raise serializers.ValidationError("Country cannot be empty.")
        return value

    def validate(self, data):
        """Perform cross-field validation if needed"""
        # Additional validation logic can be added here
        return data