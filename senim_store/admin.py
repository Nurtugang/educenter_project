from django.contrib import admin
from .models import Product, Order, OrderItem, UserCoins

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'description')
    search_fields = ('name', 'description')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'get_total')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email')
    inlines = [OrderItemInline]

    def get_queryset(self, request):
        # Фильтруем заказы, показывая только завершенные
        queryset = super().get_queryset(request)
        return queryset.filter(completed=True)

    def get_total(self, obj):
        return sum(item.product.price * item.quantity for item in obj.orderitem_set.all())
    get_total.short_description = 'Итого'


class UserCoinsAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'last_updated')
    search_fields = ('user', )

admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(UserCoins, UserCoinsAdmin)
