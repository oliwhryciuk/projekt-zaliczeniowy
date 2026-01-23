from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.http import JsonResponse, HttpResponseForbidden
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.decorators import login_required

from .models import Bag, Cart, CartItem, OrderSummary, OrderSummaryItem, Order, User_acc
from .serializers import BagSerializer, CartSerializer, OrderSummarySerializer
from .forms import CheckoutForm, CustomUserCreationForm
from .permissions import CanViewBag, CanViewCart, CanViewOrder


@api_view(['GET'])
@permission_classes([AllowAny])
def bags_list(request):
    if request.method == 'GET':
        bags = Bag.objects.all()
        serializer = BagSerializer(bags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def bags_small(request):
    if request.method == 'GET':
        bags = Bag.objects.filter(size=1)
        serializer = BagSerializer(bags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def bags_medium(request):
    if request.method == 'GET':
        bags = Bag.objects.filter(size=2)
        serializer = BagSerializer(bags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def bags_big(request):
    if request.method == 'GET':
        bags = Bag.objects.filter(size=3)
        serializer = BagSerializer(bags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cart_view(request):
    if request.method == 'GET':
        cart, _ = Cart.objects.get_or_create(user_cart=request.user.user_acc)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def summary_view(request):
    if request.method == 'GET':
        summary = OrderSummary.objects.filter(user=request.user.user_acc).order_by('-created_at').first()
        if not summary:
            return Response(
                {"error": "No summary found."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = OrderSummarySerializer(summary)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get("username")
    password = request.data.get("password")
    email = request.data.get("email")
    
    if not username or not password:
        return Response(
            {"error": "Username and password required."}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(username=username).exists():
        return Response(
            {"error": "Username already exists."}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = User.objects.create_user(username=username, password=password, email=email)
    return Response(
        {"success": True, "user_id": user.id}, 
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get("username")
    password = request.data.get("password")
    
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return Response(
            {"success": True}, 
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            {"error": "Invalid credentials."}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@csrf_exempt
def logout_view(request):
    if request.method in ['POST', 'GET']:
        logout(request)
        return redirect('store:main-page')


@api_view(['POST'])
@permission_classes([AllowAny])
def get_auth_token(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password required.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(request, username=username, password=password)
    if user is not None:
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {'token': token.key, 'user_id': user.id}, 
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            {'error': 'Invalid credentials.'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


def main_page(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('/admin/')
    return render(request, "main.html")


@csrf_protect
def login_page(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("store:main-page")
        else:
            error = "Invalid credentials."
    
    return render(request, "account/login.html", {"error": error})


def register_page(request):
    if request.user.is_authenticated:
        return redirect('store:main-page')
    
    error = None
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            if request.POST.get('password1') != request.POST.get('password2'):
                error = 'Passwords do not match.'
            else:
                user = form.save(commit=False)
                user.email = form.cleaned_data['email']
                user.save()
                
                try:
                    user_acc = user.user_acc
                    user_acc.phone_number = form.cleaned_data['phone_number']
                    user_acc.save()
                except User_acc.DoesNotExist:
                    pass
                
                login(request, user)
                return redirect('store:main-page')
        else:
            error = form.errors
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'account/register.html', {'form': form, 'error': error})


def bags_list_html(request):
    bags = Bag.objects.all()
    return render(request, "bag/detail.html", {'bags': bags})


def bag_detail_html(request, bag_id):
    bag = get_object_or_404(Bag, id=bag_id)
    error = None
    success = None
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('store:login-page')
        
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            error = 'Invalid quantity.'
            return render(request, 'bag/detail.html', {
                'bag': bag, 
                'error': error, 
                'success': success
            })
        
        if quantity < 1 or quantity > 5:
            error = 'Invalid quantity.'
        elif bag.amount < quantity:
            error = f'Not enough bags in stock. Available: {bag.amount}.'
        else:
            try:
                # Ensure User_acc exists, create if needed
                user_acc, _ = User_acc.objects.get_or_create(
                    django_user=request.user,
                    defaults={
                        'name': request.user.first_name or request.user.username,
                        'surname': request.user.last_name or request.user.username,
                        'email': request.user.email or f'{request.user.username}@example.com',
                        'street_name': 'Not provided',
                        'home_nr': '0',
                        'city': 'Not provided',
                        'zip_code': '00-000',
                        'country': 'US',
                        'phone_number': '+1234567890',
                    }
                )
                cart, _ = Cart.objects.get_or_create(user_cart=user_acc)
                item, created = CartItem.objects.get_or_create(
                    cart=cart, 
                    bag=bag, 
                    defaults={'quantity': quantity, 'price_at_time': bag.price}
                )
                
                if not created:
                    if bag.amount < item.quantity + quantity:
                        error = f'Not enough bags in stock. Available: {bag.amount - item.quantity}.'
                    else:
                        item.quantity += quantity
                        item.save()
                        success = 'Added to cart successfully!'
                else:
                    success = 'Added to cart successfully!'
            except Exception as e:
                error = f'Error adding to cart: {str(e)}'
    
    return render(request, 'bag/detail.html', {
        'bag': bag, 
        'error': error, 
        'success': success
    })


def small_bags_page(request):
    bags = Bag.objects.filter(size=1)
    return render(request, "bag/small_bags.html", {'bags': bags})


def medium_bags_page(request):
    bags = Bag.objects.filter(size=2)
    return render(request, "bag/medium_bags.html", {'bags': bags})


def big_bags_page(request):
    bags = Bag.objects.filter(size=3)
    return render(request, "bag/big_bags.html", {'bags': bags})


@login_required(login_url='store:login-page')
def cart_page(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('/admin/')
    
    try:
        # Ensure User_acc exists, create if needed
        user_acc, _ = User_acc.objects.get_or_create(
            django_user=request.user,
            defaults={
                'name': request.user.first_name or request.user.username,
                'surname': request.user.last_name or request.user.username,
                'email': request.user.email or f'{request.user.username}@example.com',
                'street_name': 'Not provided',
                'home_nr': '0',
                'city': 'Not provided',
                'zip_code': '00-000',
                'country': 'US',
                'phone_number': '+1234567890',
            }
        )
    except Exception:
        return redirect('store:login-page')
    
    cart, _ = Cart.objects.get_or_create(user_cart=user_acc)
    items = cart.items.select_related('bag').all()
    total = sum(item.quantity * item.price_at_time for item in items)
    
    return render(request, 'order/cart.html', {
        'cart': cart, 
        'items': items, 
        'total': total
    })


@login_required(login_url='store:login-page')
def checkout(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('/admin/')
    
    try:
        # Ensure User_acc exists, create if needed
        user_acc, _ = User_acc.objects.get_or_create(
            django_user=request.user,
            defaults={
                'name': request.user.first_name or request.user.username,
                'surname': request.user.last_name or request.user.username,
                'email': request.user.email or f'{request.user.username}@example.com',
                'street_name': 'Not provided',
                'home_nr': '0',
                'city': 'Not provided',
                'zip_code': '00-000',
                'country': 'US',
                'phone_number': '+1234567890',
            }
        )
    except Exception:
        return redirect('store:login-page')
    
    try:
        cart = Cart.objects.get(user_cart=user_acc)
        if not cart.items.exists():
            return redirect('store:cart')
    except Cart.DoesNotExist:
        return redirect('store:cart')
    
    form = None
    success = None
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user_acc.name = form.cleaned_data['name']
                    user_acc.surname = form.cleaned_data['surname']
                    user_acc.email = form.cleaned_data['email']
                    user_acc.street_name = form.cleaned_data['street_name']
                    user_acc.home_nr = form.cleaned_data['home_nr']
                    user_acc.city = form.cleaned_data['city']
                    user_acc.zip_code = form.cleaned_data['zip_code']
                    user_acc.country = form.cleaned_data['country']
                    user_acc.phone_number = form.cleaned_data['phone_number']
                    user_acc.save()
                    
                    total_price = sum(
                        item.quantity * item.price_at_time 
                        for item in cart.items.all()
                    )
                    order = Order.objects.create(
                        user=user_acc,
                        total_price=total_price,
                        status='new'
                    )
                    
                    # Update bag quantities in inventory
                    for item in cart.items.all():
                        bag = item.bag
                        bag.amount -= item.quantity
                        if bag.amount < 0:
                            bag.amount = 0
                        bag.save()
                    
                    cart.items.all().delete()
                
                return render(request, 'order/checkout.html', {
                    'user_acc': user_acc,
                    'form': form,
                    'success': True,
                    'order_id': order.id
                })
            except Exception as e:
                form.add_error(None, f'Error placing order: {str(e)}')
    else:
        form = CheckoutForm(initial={
            'name': user_acc.name,
            'surname': user_acc.surname,
            'email': user_acc.email,
            'street_name': user_acc.street_name,
            'home_nr': user_acc.home_nr,
            'city': user_acc.city,
            'zip_code': user_acc.zip_code,
            'country': user_acc.country,
            'phone_number': user_acc.phone_number
        })
    
    return render(request, 'order/checkout.html', {
        'user_acc': user_acc,
        'form': form,
        'success': success
    })


@transaction.atomic
def go_to_order_summary(request):
    if not request.user.is_authenticated:
        return redirect('store:login-page')
    
    user = request.user.user_acc
    
    try:
        cart = Cart.objects.get(user_cart=user)
    except Cart.DoesNotExist:
        return redirect('store:cart')
    
    summary = OrderSummary.objects.create(user=user)
    total = 0
    
    for item in cart.items.all():
        OrderSummaryItem.objects.create(
            summary=summary,
            bag=item.bag,
            quantity=item.quantity,
            price_at_time=item.price_at_time
        )
        total += item.quantity * item.price_at_time
    
    summary.total_price = total
    summary.save()
    
    return redirect('store:order-summary')


