from django import forms 
from django.core.exceptions import ValidationError
from .models import Bag, User_acc
import re

def validate_name_starts_with_capital(value):
    """Validate that name starts with a capital letter"""
    if not value:
        raise ValidationError("This field cannot be empty.")
    if not value[0].isupper():
        raise ValidationError("Name must start with a capital letter.")
    if not re.match(r"^[A-Z][a-zA-Z\s'-]*$", value):
        raise ValidationError("Name can only contain letters, spaces, hyphens, and apostrophes.")

def validate_email_format(value):
    """Validate email format"""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, value):
        raise ValidationError("Please enter a valid email address.")

def validate_phone_number(value):
    """Validate phone number format"""
    cleaned = re.sub(r'[\s\-+()]', '', str(value))
    if not cleaned.isdigit() or len(cleaned) < 9:
        raise ValidationError("Phone number must contain at least 9 digits.")

def validate_zip_code(value):
    """Validate zip code format (Polish format XX-XXX or other common formats)"""
    if not re.match(r'^[0-9]{2}-?[0-9]{3}$|^[0-9]{5}$|^[A-Z0-9\s-]{3,10}$', value):
        raise ValidationError("Please enter a valid zip code.")

def validate_not_empty(value):
    """Validate that field is not empty"""
    if not value or not str(value).strip():
        raise ValidationError("This field cannot be empty.")

class BagForm(forms.ModelForm):
    class Meta:
        model = Bag
        fields = ['model', 'brand', 'size', 'color', 'fabric', 'price']

class CheckoutForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        validators=[validate_name_starts_with_capital],
        label="First Name"
    )
    surname = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        validators=[validate_name_starts_with_capital],
        label="Last Name"
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        validators=[validate_email_format],
        label="Email"
    )
    street_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        validators=[validate_not_empty],
        label="Street Name"
    )
    home_nr = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        validators=[validate_not_empty],
        label="House Number"
    )
    city = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        validators=[validate_not_empty],
        label="City"
    )
    zip_code = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        validators=[validate_zip_code],
        label="Zip Code"
    )
    country = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        validators=[validate_not_empty],
        label="Country"
    )
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'tel'}),
        validators=[validate_phone_number],
        label="Phone Number"
    )