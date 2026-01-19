from django import forms 
from django_countries.fields import CountryField
from .models import Bag, User_acc
from .serializers import (
    validate_name_starts_with_capital,
    validate_email_format,
    validate_phone_number,
    validate_zip_code,
    validate_not_empty
)


class BagForm(forms.ModelForm):
    class Meta:
        model = Bag
        fields = ['model_name', 'brand', 'size', 'color', 'fabric', 'price']

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
    country = CountryField().formfield(
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Country"
    )
    phone_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'tel'}),
        validators=[validate_phone_number],
        label="Phone Number"
    )