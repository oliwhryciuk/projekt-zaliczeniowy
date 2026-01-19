from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Bag, User_acc, Cart, CartItem, OrderSummary, OrderSummaryItem, Order, SIZE, COLOR, FABRIC
import re

ZIP_PL_REGEX = r"^\d{2}-\d{3}$"
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
NAME_REGEX = r"^[A-Z][a-zA-Z\s'-]*$"
ZIP_CODE_REGEX = r'^[0-9]{2}-?[0-9]{3}$|^[0-9]{5}$|^[A-Z0-9\s-]{3,10}$'

def validate_name_starts_with_capital(value):
    """
    Validate that name starts with a capital letter.
    Used for first name and last name fields.
    """
    if not value:
        raise DjangoValidationError("This field cannot be empty.")
    value_str = str(value).strip()
    if not value_str:
        raise DjangoValidationError("This field cannot be empty.")
    if not value_str[0].isupper():
        raise DjangoValidationError("Name must start with a capital letter.")
    if not re.match(NAME_REGEX, value_str):
        raise DjangoValidationError("Name can only contain letters, spaces, hyphens, and apostrophes.")
    return value

def validate_email_format(value):
    """Validate email format."""
    if not value:
        raise DjangoValidationError("Email cannot be empty.")
    value_str = str(value).strip()
    if not re.match(EMAIL_REGEX, value_str):
        raise DjangoValidationError("Please enter a valid email address.")
    return value

def validate_phone_number(value):
    """
    Validate phone number format.
    Must contain at least 9 digits.
    """
    if not value:
        raise DjangoValidationError("Phone number cannot be empty.")
    # Remove spaces, dashes, and plus signs for checking
    cleaned = re.sub(r'[\s\-+()]', '', str(value))
    if not cleaned.isdigit() or len(cleaned) < 9:
        raise DjangoValidationError("Phone number must contain at least 9 digits.")
    return value

def validate_zip_code(value):
    """
    Validate zip code format.
    Supports Polish format (XX-XXX), 5-digit format, and other international formats.
    """
    if not value:
        raise DjangoValidationError("Zip code cannot be empty.")
    value_str = str(value).strip()
    if not re.match(ZIP_CODE_REGEX, value_str):
        raise DjangoValidationError("Please enter a valid zip code.")
    return value

def validate_not_empty(value):
    """Validate that field is not empty."""
    if not value:
        raise DjangoValidationError("This field cannot be empty.")
    value_str = str(value).strip()
    if not value_str:
        raise DjangoValidationError("This field cannot be empty.")
    return value

class BagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bag
        fields = "__all__"

    def validate_model_name(self, value):
        value = str(value).strip()
        if not value:
            raise serializers.ValidationError("Model name cannot be empty.")
        if not value[0].isupper():
            raise serializers.ValidationError("Model name must start with an uppercase letter.")
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
        try:
            validate_name_starts_with_capital(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(str(e))
        return str(value).strip()

    def validate_surname(self, value):
        try:
            validate_name_starts_with_capital(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(str(e))
        return str(value).strip()

    def validate_email(self, value):
        try:
            validate_email_format(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(str(e))
        return str(value).strip().lower()

    def validate_zip_code(self, value):
        try:
            validate_zip_code(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(str(e))
        return str(value).strip()

    def validate_phone_number(self, value):
        try:
            validate_phone_number(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(str(e))
        return value
    
    def validate(self, data):
        # Additional validation for non-empty fields
        for field_name in ['street_name', 'home_nr', 'city', 'country']:
            if field_name in data:
                try:
                    validate_not_empty(data[field_name])
                except DjangoValidationError as e:
                    raise serializers.ValidationError({field_name: str(e)})
        return data


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