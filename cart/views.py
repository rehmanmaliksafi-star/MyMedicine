from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Cart, CartItem
from core.models import Product, Prescription
import json

@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all().select_related('product', 'product__category')
    subtotal = cart.get_total()
    shipping = 0 if subtotal >= 2000 else 150
    total = subtotal + shipping
    return render(request, 'cart/cart.html', {
        'cart': cart, 'cart_items': cart_items,
        'subtotal': subtotal, 'shipping': shipping,
        'free_shipping': shipping == 0,
        'free_shipping_remaining': max(0, 2000 - subtotal),
        'total': total, 'item_count': cart.get_item_count(),
    })

@login_required
def add_to_cart(request, product_id=None):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    pid = request.POST.get('product_id') or request.GET.get('product_id') or product_id
    quantity = int(request.POST.get('quantity', 1))
    product = get_object_or_404(Product, id=pid, is_active=True)

    if product.stock < quantity:
        msg = f'Only {product.stock} item(s) in stock.'
        if is_ajax: return JsonResponse({'status': 'error', 'message': msg}, status=400)
        messages.error(request, msg); return redirect('product_detail', slug=product.slug)

    if product.needs_prescription:
        has_rx = Prescription.objects.filter(user=request.user, product=product, status='approved').exists()
        if not has_rx:
            if is_ajax:
                return JsonResponse({'status': 'prescription_required', 'message': 'This product requires a valid prescription.', 'redirect_url': f'/upload-prescription/?product_id={product.id}'}, status=403)
            messages.warning(request, 'Prescription required. Please upload yours first.')
            return redirect(f'/upload-prescription/?product_id={product.id}')

    cart, _ = Cart.objects.get_or_create(user=request.user)
    item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': quantity})
    if not created:
        item.quantity += quantity; item.save()

    if is_ajax:
        return JsonResponse({'status': 'success', 'message': f'{product.name} added to cart!', 'cart_count': cart.get_item_count()})
    messages.success(request, f'{product.name} added to cart!')
    return redirect(request.POST.get('next', 'cart_view'))

@login_required
def update_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        item_id = data.get('item_id')
        quantity = int(data.get('quantity', 1))
        item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        if quantity < 1:
            item.delete()
        elif quantity > item.product.stock:
            return JsonResponse({'status': 'error', 'message': f'Only {item.product.stock} in stock.'}, status=400)
        else:
            item.quantity = quantity; item.save()
        cart = Cart.objects.get(user=request.user)
        return JsonResponse({'status': 'success', 'cart_count': cart.get_item_count(), 'cart_total': float(cart.get_total())})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    name = item.product.name; item.delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cart = Cart.objects.get(user=request.user)
        return JsonResponse({'status': 'success', 'message': f'{name} removed.', 'cart_count': cart.get_item_count()})
    messages.success(request, f'{name} removed.'); return redirect('cart_view')

@login_required
def clear_cart(request):
    cart = Cart.objects.filter(user=request.user).first()
    if cart: cart.items.all().delete()
    messages.success(request, 'Cart cleared.'); return redirect('cart_view')
