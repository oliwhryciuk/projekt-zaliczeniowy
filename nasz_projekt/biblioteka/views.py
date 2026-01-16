from django.shortcuts import render
from django.db import transaction
from django.shortcuts import redirect



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
        OrderItem.objects.create(
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

