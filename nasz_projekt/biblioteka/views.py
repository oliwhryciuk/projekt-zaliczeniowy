from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.http import JsonResponse, HttpResponseForbidden
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Bag, Cart, CartItem, OrderSummary, OrderSummaryItem, Order, User_acc
from .serializers import BagSerializer, CartSerializer, OrderSummarySerializer
from .forms import CheckoutForm, CustomUserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework import status
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token

@transaction.atomic
def go_to_order_summary(request):
    user = request.user.user_acc
    cart = Cart.objects.get(user_cart=user)

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

    return redirect("order_summary_detail", summary_id=summary.id)

def checkout(request):
    # Redirect admins to admin page
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('/admin/')
    
    # Redirect non-authenticated users to login
    if not request.user.is_authenticated:
        return redirect('/login-page')
    
    try:
        user_acc = request.user.user_acc
    except Exception:
        return redirect('/login-page')
    
    try:
        cart = Cart.objects.get(user_cart=user_acc)
        if not cart.items.exists():
            return redirect('/cart')
    except Cart.DoesNotExist:
        return redirect('/cart')
    
    form = None
    success = None
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
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
                
                total_price = sum(item.quantity * item.price_at_time for item in cart.items.all())
                order = Order.objects.create(
                    user=user_acc,
                    total_price=total_price,
                    status='new'
                )
                
                cart.items.all().delete()
                
                return render(request, 'checkout.html', {
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
    
    return render(request, 'checkout.html', {
        'user_acc': user_acc,
        'form': form,
        'success': success
    })

@api_view(["GET"])
def bags_list(request):
    bags = Bag.objects.all()
    serializer = BagSerializer(bags, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(["GET"])
def bags_small(request):
    bags = Bag.objects.filter(size=1)  # mini
    serializer = BagSerializer(bags, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(["GET"])
def bags_medium(request):
    bags = Bag.objects.filter(size=2)  # midi
    serializer = BagSerializer(bags, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(["GET"])
def bags_big(request):
    bags = Bag.objects.filter(size=3)  # maxi
    serializer = BagSerializer(bags, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get("username")
    password = request.data.get("password")
    email = request.data.get("email")
    if not username or not password:
        return JsonResponse({"error": "Username and password required."}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({"error": "Username already exists."}, status=400)
    user = User.objects.create_user(username=username, password=password, email=email)
    return JsonResponse({"success": True, "user_id": user.id})

@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return JsonResponse({"success": True})
    else:
        return JsonResponse({"error": "Invalid credentials."}, status=400)

@csrf_exempt
def logout_view(request):
    from django.contrib.auth import logout
    if request.method == 'POST' or request.method == 'GET':
        logout(request)
        return redirect('/')

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user_cart=request.user.user_acc)
    serializer = CartSerializer(cart)
    return JsonResponse(serializer.data, safe=False)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def summary_view(request):
    summary = OrderSummary.objects.filter(user=request.user.user_acc).order_by('-created_at').first()
    if not summary:
        return JsonResponse({"error": "No summary found."}, status=404)
    serializer = OrderSummarySerializer(summary)
    return JsonResponse(serializer.data, safe=False)

@api_view(['POST'])
@permission_classes([AllowAny])
def get_auth_token(request):
    """Generate or retrieve auth token for a user"""
    username = request.data.get('username')
    password = request.data.get('password')
    if not username or not password:
        return JsonResponse({'error': 'Username and password required.'}, status=400)
    user = authenticate(request, username=username, password=password)
    if user is not None:
        token, created = Token.objects.get_or_create(user=user)
        return JsonResponse({'token': token.key, 'user_id': user.id})
    else:
        return JsonResponse({'error': 'Invalid credentials.'}, status=400)

def main_page(request):
    # Redirect admins to admin page
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('/admin/')
    return render(request, "main.html")

@csrf_protect
def login_page(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        from django.contrib.auth import authenticate, login
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("main_page")
        else:
            error = "Invalid credentials."
    return render(request, "login.html", {"error": error})

def register(request):
    if request.user.is_authenticated:
        return redirect('/')
    error = None
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Check if passwords match
            if request.POST.get('password1') != request.POST.get('password2'):
                error = 'Passwords do not match.'
            else:
                user = form.save(commit=False)
                user.email = form.cleaned_data['email']
                user.save()
                
                # Save phone number to User_acc
                try:
                    user_acc = user.user_acc
                    user_acc.phone_number = form.cleaned_data['phone_number']
                    user_acc.save()
                except User_acc.DoesNotExist:
                    pass
                
                login(request, user)
                return redirect('/')
        else:
            error = form.errors
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form, 'error': error})

def small_bags_page(request):
    return render(request, "small_bags.html")

def medium_bags_page(request):
    return render(request, "medium_bags.html")

def big_bags_page(request):
    return render(request, "big_bags.html")

def bag_detail(request, bag_id):
    from .models import Bag, Cart, CartItem, User_acc
    bag = get_object_or_404(Bag, id=bag_id)
    error = None
    success = None
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('/login-page')
        try:
            user_acc = User_acc.objects.get(django_user=request.user)
        except User_acc.DoesNotExist:
            return redirect('/login-page')
        try:
            quantity = int(request.POST.get('quantity', 1))
        except ValueError:
            error = 'Invalid quantity.'
            return render(request, 'bag_detail.html', {'bag': bag, 'error': error, 'success': success})
        if quantity < 1 or quantity > 5:
            error = 'Invalid quantity.'
        elif bag.amount < quantity:
            error = f'Not enough bags in stock. Available: {bag.amount}.'
        else:
            cart, _ = Cart.objects.get_or_create(user_cart=user_acc)
            item, created = CartItem.objects.get_or_create(cart=cart, bag=bag, defaults={'quantity': quantity, 'price_at_time': bag.price})
            if not created:
                if bag.amount < item.quantity + quantity:
                    error = f'Not enough bags in stock. Available: {bag.amount - item.quantity}.'
                else:
                    item.quantity += quantity
                    item.save()
                    success = 'Added to cart successfully!'
            else:
                success = 'Added to cart successfully!'
    return render(request, 'bag_detail.html', {'bag': bag, 'error': error, 'success': success})

def cart_page(request):
    # Redirect admins to admin page
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('/admin/')
    
    # Redirect non-authenticated users to login
    if not request.user.is_authenticated:
        return redirect('/login-page')
    
    try:
        user_acc = request.user.user_acc
    except Exception:
        return redirect('/login-page')
    
    cart, _ = Cart.objects.get_or_create(user_cart=user_acc)
    items = cart.items.select_related('bag').all()
    total = sum(item.quantity * item.price_at_time for item in items)
    return render(request, 'cart.html', {'cart': cart, 'items': items, 'total': total})

