from django.shortcuts import get_object_or_404, render
from .models import Order, OrderItem, Product, UserCoins
from django.http import JsonResponse
from django.db import transaction
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

@require_POST
def order_success(request):
    try:
        order = Order.objects.get(user=request.user, completed=False)
        total_price = sum(item.product.price * item.quantity for item in order.orderitem_set.all())
        user_coins = UserCoins.objects.get(user=request.user)

        with transaction.atomic():
            if user_coins.balance >= total_price:
                # Обновляем баланс и помечаем заказ как завершенный
                user_coins.balance -= total_price
                user_coins.save()

                # Завершаем заказ
                order.completed = True
                order.save()

                # Возвращаем успешный ответ и обновленный баланс
                return JsonResponse({
                    'status': 'success',
                    'message': 'Заказ успешно оформлен',
                    'balance': user_coins.balance
                }, status=200)
            else:
                # Если недостаточно коинов
                return JsonResponse({
                    'status': 'error',
                    'message': 'Недостаточно коинов для оформления заказа',
                    'balance': user_coins.balance
                }, status=400)

    except Order.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Заказ не найден'}, status=404)

@login_required
def product_list(request):
    products = Product.objects.all()
    if UserCoins.objects.filter(user=request.user).exists() == False:
        UserCoins.objects.create(user=request.user)
    return render(request, 'product_list.html', {'products': products})


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    order, created = Order.objects.get_or_create(user=request.user, completed=False)
    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

    if not created:
        order_item.quantity += 1
    order_item.save()

    return JsonResponse({
        'cart_count': order.orderitem_set.count(),
        'cart_total': sum(item.product.price * item.quantity for item in order.orderitem_set.all())
    })

@login_required
def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    order = Order.objects.get(user=request.user, completed=False)
    order_item = get_object_or_404(OrderItem, order=order, product=product)
    order_item.delete()

    return JsonResponse({
        'cart_count': order.orderitem_set.count(),
        'cart_total': sum(item.product.price * item.quantity for item in order.orderitem_set.all())
    })


def get_cart_items(request):
    order = Order.objects.get(user=request.user, completed=False)
    order_items = order.orderitem_set.all()

    items = []
    for item in order_items:
        items.append({
            'product_id': item.product.id,
            'product_name': item.product.name,
            'product_price': item.product.price,
            'quantity': item.quantity,
            'item_total': item.quantity * item.product.price,
            'product_image': item.product.image.url,
        })

    return JsonResponse({
        'items': items,
        'cart_total': sum(item.product.price * item.quantity for item in order_items),
        'cart_count': order_items.count()
    })
