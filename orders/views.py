from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Order, OrderItem
from cart.models import Cart

@login_required
def checkout_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all().select_related('product')
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty.'); return redirect('cart_view')
    subtotal = cart.get_total()
    shipping = 0 if subtotal >= 2000 else 150
    total = subtotal + shipping
    if request.method == 'POST':
        full_name = request.POST.get('full_name','').strip()
        email = request.POST.get('email','').strip()
        phone = request.POST.get('phone','').strip()
        address = request.POST.get('address','').strip()
        city = request.POST.get('city','').strip()
        if not all([full_name, email, phone, address, city]):
            messages.error(request, 'Please fill in all required fields.')
        else:
            order = Order.objects.create(
                user=request.user, full_name=full_name, email=email, phone=phone,
                address=address, city=city, postal_code=request.POST.get('postal_code','').strip(),
                total_amount=total, payment_method=request.POST.get('payment_method','cash'),
                payment_status='paid' if request.POST.get('payment_method') == 'simulated' else 'pending',
                notes=request.POST.get('notes','').strip(),
            )
            for item in cart_items:
                OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, price=item.product.final_price)
                p = item.product; p.stock = max(0, p.stock - item.quantity); p.save(update_fields=['stock'])
            cart.items.all().delete()
            if request.POST.get('payment_method') == 'easypaisa':
                # Pay on Easypaisa's secure page; order stays pending until
                # the gateway callback confirms the payment.
                return redirect('payments:easypaisa_start', order_id=order.id)
            messages.success(request, f'Order #{order.order_number} placed successfully!')
            return redirect('order_confirmation', order_id=order.id)
    return render(request, 'orders/checkout.html', {'cart_items': cart_items, 'subtotal': subtotal, 'shipping': shipping, 'total': total})

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/confirmation.html', {'order': order})

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    return render(request, 'orders/my_orders.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})
