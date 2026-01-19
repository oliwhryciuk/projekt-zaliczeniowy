from django.shortcuts import render
from django.db import transaction
from django.shortcuts import redirect
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Bag, Cart, CartItem, OrderSummary, OrderSummaryItem, Order
from .serializers import BagSerializer, CartSerializer, OrderSummarySerializer
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework import status
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_protect


#dodawanie rzeczy do koszyka wzięte z czata, moze do zmiany
def add_to_cart(user, bag_id):
    cart, created = Cart.objects.get_or_create(user=user)
    bag = Bag.objects.get(id=bag_id)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        bag=bag,
        defaults={
            "quantity": 1,
            "price_at_time": bag.price
        }
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()


def cart_total(cart):
    return sum(
        item.quantity * item.price_at_time
        for item in cart.items.all()
    )

# koniec dodawania rzeczy ^

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


#widok szczegółów podsumowania zamówienia
def order_summary_detail(request, summary_id):
    summary = OrderSummary.objects.get(
        id=summary_id,
        user=request.user.user_acc
    )
    return render(
        request,
        "order_summary.html",
        {"summary": summary}
    )


@transaction.atomic
def checkout(request, summary_id):
    user = request.user.user_acc
    summary = OrderSummary.objects.select_for_update().get(
        id=summary_id,
        user=user
    )

    #  sprawdź magazyn
    for item in summary.items.select_for_update():
        if item.quantity > item.bag.amount:
            raise ValidationError(
                f"Brak towaru: {item.bag}"
            )

    #  utwórz Order
    order = Order.objects.create(
        user=user,
        total_price=summary.total_price
    )

    #  przenieś pozycje + zmniejsz magazyn
    for item in summary.items.all():
        OrderSummaryItem.objects.create(
            order=order,
            bag=item.bag,
            quantity=item.quantity,
            price_at_time=item.price_at_time
        )

        item.bag.amount -= item.quantity
        item.bag.save()

    # 4usuń koszyk
    Cart.objects.filter(user_cart=user).delete()

    #  usuń podsumowanie
    summary.delete()

    return redirect("order_success", order_id=order.id)


# --- API ENDPOINTS ---

@api_view(["GET"])
def bags_list(request):
    bags = Bag.objects.all()
    serializer = BagSerializer(bags, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(["GET"])
def bags_small(request):
    bags = Bag.objects.filter(size=0)  # mini
    serializer = BagSerializer(bags, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(["GET"])
def bags_medium(request):
    bags = Bag.objects.filter(size=1)  # midi
    serializer = BagSerializer(bags, many=True)
    return JsonResponse(serializer.data, safe=False)

@api_view(["GET"])
def bags_big(request):
    bags = Bag.objects.filter(size=2)  # maxi
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

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return JsonResponse({"success": True})

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

def main_page(request):
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

