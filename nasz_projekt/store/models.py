from django.db import models
from django.contrib.auth.models import User
from django import forms 
from django_countries.fields import CountryField
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


SIZE = models.IntegerChoices(
    'SIZE',
    'mini midi maxi'
)

COLOR = models.IntegerChoices(
    'COLOR',
    'beige white brown black red purple blue orange pink gold silver grey green yellow mixed '
)

FABRIC = models.IntegerChoices(
    'FABRIC',
    'natural_leather vegan_leather cotton nylon vinyl jute canvas'
)


class Bag(models.Model):
    model_name = models.CharField(max_length= 100, null = False,  blank = False )
    brand =  models.CharField(max_length= 50, null = False,  blank = False )
    size = models.IntegerField(choices = SIZE.choices, default= SIZE.choices[2][0])
    color = models.IntegerField(choices = COLOR.choices, default= COLOR.choices[14][0])
    fabric = models.IntegerField(choices = FABRIC.choices, default= FABRIC.choices[6][0])
    price = models.PositiveIntegerField(null=False, blank=False, verbose_name="price in zł")
    amount = models.PositiveIntegerField() 
    photo = models.ImageField(upload_to='bag_photos/', null=True, blank=True)

    def __str__(self):
        return f"{self.brand} {self.model_name}"
    

class User_acc(models.Model):
    django_user = models.OneToOneField(User, on_delete = models.CASCADE)
    name = models.CharField(max_length= 100, null = False,  blank = False )
    surname = models.CharField(max_length= 100, null = False,  blank = False )
    email = models.EmailField(unique = True, null = False,  blank = False )
    street_name = models.CharField(max_length= 100, null = False,  blank = False )
    home_nr = models.CharField(max_length= 10, null = False,  blank = False )
    city = models.CharField(max_length= 100, null = False,  blank = False )
    zip_code = models.CharField(max_length= 6, null = False,  blank = False )
    country = CountryField(blank=False)
    phone_number = PhoneNumberField(blank = False, null = False)


class Cart(models.Model):
    user_cart = models.OneToOneField(User_acc, on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart {self.user_cart}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete = models.CASCADE, related_name="items")
    bag = models.ForeignKey(Bag, on_delete = models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time = models.PositiveIntegerField()

    class Meta:
        unique_together = ("cart", "bag")

    def __str__(self):
        return f"{self.bag} x {self.quantity}"


class OrderSummary(models.Model):
    user = models.ForeignKey(User_acc, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Order Summary {self.id}"


class OrderSummaryItem(models.Model):
    summary = models.ForeignKey(OrderSummary, on_delete=models.CASCADE, related_name="items")
    bag = models.ForeignKey(Bag, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price_at_time = models.PositiveIntegerField()


class Order(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        SENT = "sent", "Sent"
        DONE = "done", "Completed"
        CANCELED = "canceled", "Canceled"

    user = models.ForeignKey(User_acc, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.NEW)

    def __str__(self):
        return f"Order #{self.id}"


@receiver(post_save, sender=User)
def create_user_account(sender, instance, created, **kwargs):
    if created:
        try:
            User_acc.objects.get_or_create(
                django_user=instance,
                defaults={
                    'name': instance.first_name or instance.username,
                    'surname': instance.last_name or instance.username,
                    'email': instance.email or f'{instance.username}@example.com',
                    'street_name': 'Not provided',
                    'home_nr': '0',
                    'city': 'Not provided',
                    'zip_code': '00-000',
                    'country': 'US',
                    'phone_number': '+1234567890',
                }
            )
        except Exception:
            pass
        
        Token.objects.get_or_create(user=instance)

post_save.connect(create_user_account, sender=User)

