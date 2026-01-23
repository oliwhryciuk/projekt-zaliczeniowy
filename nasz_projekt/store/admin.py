from django.contrib import admin
from .models import Bag
from .models import Order, OrderSummary, OrderSummaryItem
from .models import User_acc
from .models import Cart, CartItem


admin.site.register(Bag)
admin.site.register(Order)
admin.site.register(OrderSummary)
admin.site.register(OrderSummaryItem)
admin.site.register(User_acc)
admin.site.register(Cart)
admin.site.register(CartItem)


class OrderItemInline(admin.TabularInline):
    model = OrderSummaryItem
    extra = 0
    readonly_fields = ("bag", "quantity", "price_at_time")
    can_delete = False


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "total_price",
        "status",
        "created_at",
    )

    list_filter = ("status", "created_at")
    search_fields = ("id", "user__email")
    ordering = ("-created_at",)

    inlines = [OrderItemInline]

    readonly_fields = ("user", "total_price", "created_at")

    fieldsets = (
        ("Informacje podstawowe", {
            "fields": ("user", "status", "created_at")
        }),
        ("Kwota", {
            "fields": ("total_price",)
        }),
    )
