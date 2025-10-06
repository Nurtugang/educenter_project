from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Order, OrderItem, UserCoins

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'description')
    search_fields = ('name', 'description')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('get_item_total',)
    fields = ('product', 'quantity', 'get_item_total')

    def get_item_total(self, obj):
        if obj.pk:
            return obj.product.price * obj.quantity
        return 0
    get_item_total.short_description = 'Сумма'

class OrderAdmin(admin.ModelAdmin):
    list_display = ('get_customer_name', 'created_at', 'get_total', 'get_items_list', 'completed')
    list_filter = ('created_at', 'completed')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    inlines = [OrderItemInline]
    list_editable = ('completed',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.prefetch_related('orderitem_set__product', 'user')

    def get_customer_name(self, obj):
        """Отображает имя и фамилию пользователя"""
        if obj.user.first_name and obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return obj.user.username
    get_customer_name.short_description = 'Заказчик'

    def get_total(self, obj):
        """Вычисляет общую сумму заказа"""
        return sum(item.product.price * item.quantity for item in obj.orderitem_set.all())
    get_total.short_description = 'Итого'

    def get_items_list(self, obj):
        """Отображает список товаров в заказе прямо в таблице"""
        items = []
        for item in obj.orderitem_set.all():
            items.append(f"{item.product.name} x{item.quantity}")
        
        if len(items) > 3:
            displayed_items = items[:3]
            remaining_count = len(items) - 3
            items_text = "<br>".join(displayed_items) + f"<br>... и еще {remaining_count}"
        else:
            items_text = "<br>".join(items)
        
        return format_html(items_text) if items else "Нет товаров"
    get_items_list.short_description = 'Товары'


class UserCoinsAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'last_updated')
    search_fields = ('user__username', 'user__first_name', 'user__last_name')

admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(UserCoins, UserCoinsAdmin)