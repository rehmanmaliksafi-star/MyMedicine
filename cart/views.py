from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import Cart, CartItem
from core.models import Product, Prescription
import json

SESSION_KEY = 'guest_cart'  # {str(product_id): quantity}


class SessionCartItem:
    """Lightweight stand-in for CartItem so a guest (session) cart renders
    in the same cart template (uses .id, .product, .quantity, .get_total())."""
    def __init__(self, product, quantity):
        self.id = f'guest-{product.id}'
        self.product = product
        self.quantity = quantity

    def get_total(self):
        return self.product.final_price * self.quantity


def _get_session_cart(request):
    data = request.session.get(SESSION_KEY, {}) or {}
    clean = {}
    for k, v in data.items():
        try:
            qty = int(v)
            if qty > 0:
                clean[str(int(k))] = qty
        except (TypeError, ValueError):
            continue
    return clean


def _save_session_cart(request, data):
    request.session[SESSION_KEY] = data
    request.session.modified = True


def _session_cart_items(request):
    """(items, subtotal, count) for a guest's session cart."""
    items, subtotal, count = [], 0, 0
    data = _get_session_cart(request)
    if data:
        products = Product.objects.filter(
            id__in=[int(k) for k in data], is_active=True
        ).select_related('category')
        by_id = {p.id: p for p in products}
        for pid_str, qty in data.items():
            product = by_id.get(int(pid_str))
            if not product:
                continue
            qty = min(qty, product.stock) if product.stock else qty
            item = SessionCartItem(product, qty)
            items.append(item)
            subtotal += item.get_total()
            count += qty
    return items, subtotal, count


def _session_cart_count(request):
    return sum(_get_session_cart(request).values())


def _merge_session_cart(request):
    """Move a guest (session) cart into the signed-in user's DB cart."""
    data = _get_session_cart(request)
    if not data:
        return
    cart, _ = Cart.objects.get_or_create(user=request.user)
    for pid_str, qty in data.items():
        try:
            product = Product.objects.get(id=int(pid_str), is_active=True)
        except Product.DoesNotExist:
            continue
        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product,
            defaults={'quantity': min(qty, product.stock)})
        if not created:
            item.quantity = min(item.quantity + qty, product.stock)
            item.save()
    request.session.pop(SESSION_KEY, None)


def _cart_summary(request):
    """(items, subtotal, count) for the current visitor, signed-in or guest."""
    if request.user.is_authenticated:
        _merge_session_cart(request)
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = list(cart.items.all().select_related('product', 'product__category'))
        return items, cart.get_total(), cart.get_item_count()
    return _session_cart_items(request)


def _cart_count(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        return cart.get_item_count() if cart else 0
    return _session_cart_count(request)


def cart_view(request):
    cart_items, subtotal, item_count = _cart_summary(request)
    shipping = 0 if subtotal >= 2000 else 150
    total = subtotal + shipping
    return render(request, 'cart/cart.html', {
        'cart_items': cart_items,
        'subtotal': subtotal, 'shipping': shipping,
        'free_shipping': shipping == 0,
        'free_shipping_remaining': max(0, 2000 - subtotal),
        'total': total, 'item_count': item_count,
    })


def add_to_cart(request, product_id=None):
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    pid = request.POST.get('product_id') or request.GET.get('product_id') or product_id
    try:
        quantity = max(1, int(request.POST.get('quantity', 1)))
    except (TypeError, ValueError):
        quantity = 1
    product = get_object_or_404(Product, id=pid, is_active=True)

    if product.stock < quantity:
        msg = f'Only {product.stock} item(s) in stock.'
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': msg}, status=400)
        messages.error(request, msg)
        return redirect('product_detail', slug=product.slug)

    if product.needs_prescription:
        if not request.user.is_authenticated:
            msg = 'Please sign in to buy prescription medicines.'
            if is_ajax:
                return JsonResponse(
                    {'status': 'login_required', 'message': msg,
                     'redirect_url': f'/accounts/login/?next=/products/{product.slug}/'},
                    status=401)
            messages.info(request, msg)
            return redirect(f'/accounts/login/?next=/products/{product.slug}/')
        has_rx = Prescription.objects.filter(
            user=request.user, product=product, status='approved').exists()
        if not has_rx:
            if is_ajax:
                return JsonResponse(
                    {'status': 'prescription_required',
                     'message': 'This product requires a valid prescription.',
                     'redirect_url': f'/upload-prescription/?product_id={product.id}'},
                    status=403)
            messages.warning(request, 'Prescription required. Please upload yours first.')
            return redirect(f'/upload-prescription/?product_id={product.id}')

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(
            cart=cart, product=product, defaults={'quantity': quantity})
        if not created:
            item.quantity += quantity
            item.save()
        count = cart.get_item_count()
    else:
        data = _get_session_cart(request)
        data[str(product.id)] = data.get(str(product.id), 0) + quantity
        _save_session_cart(request, data)
        count = sum(data.values())

    if is_ajax:
        return JsonResponse({'status': 'success',
                             'message': f'{product.name} added to cart!',
                             'cart_count': count})
    messages.success(request, f'{product.name} added to cart!')
    return redirect(request.POST.get('next', 'cart_view'))


def update_cart(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error'}, status=400)
    try:
        data = json.loads(request.body)
        item_id = str(data.get('item_id'))
        quantity = int(data.get('quantity', 1))
    except (TypeError, ValueError):
        return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)

    if item_id.startswith('guest-'):
        session = _get_session_cart(request)
        pid = item_id.split('-', 1)[1]
        if pid not in session:
            return JsonResponse({'status': 'error', 'message': 'Item not in cart.'}, status=404)
        if quantity < 1:
            del session[pid]
        else:
            product = get_object_or_404(Product, id=pid, is_active=True)
            if quantity > product.stock:
                return JsonResponse(
                    {'status': 'error',
                     'message': f'Only {product.stock} in stock.'}, status=400)
            session[pid] = quantity
        _save_session_cart(request, session)
        items, subtotal, count = _session_cart_items(request)
        return JsonResponse({'status': 'success', 'cart_count': count,
                             'cart_total': float(subtotal)})

    if not request.user.is_authenticated:
        return JsonResponse({'status': 'login_required',
                             'message': 'Please sign in to update your cart.'}, status=401)
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if quantity < 1:
        item.delete()
    elif quantity > item.product.stock:
        return JsonResponse({'status': 'error',
                             'message': f'Only {item.product.stock} in stock.'}, status=400)
    else:
        item.quantity = quantity
        item.save()
    cart = Cart.objects.get(user=request.user)
    return JsonResponse({'status': 'success', 'cart_count': cart.get_item_count(),
                         'cart_total': float(cart.get_total())})


def remove_from_cart(request, item_id):
    item_id = str(item_id)
    if item_id.startswith('guest-'):
        session = _get_session_cart(request)
        pid = item_id.split('-', 1)[1]
        product = Product.objects.filter(id=pid).first()
        name = product.name if product else 'Item'
        session.pop(pid, None)
        _save_session_cart(request, session)
        count = sum(session.values())
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': f'{name} removed.',
                                 'cart_count': count})
        messages.success(request, f'{name} removed.')
        return redirect('cart_view')

    if not request.user.is_authenticated:
        return redirect('login')
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    name = item.product.name
    item.delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cart = Cart.objects.get(user=request.user)
        return JsonResponse({'status': 'success', 'message': f'{name} removed.',
                             'cart_count': cart.get_item_count()})
    messages.success(request, f'{name} removed.')
    return redirect('cart_view')


def clear_cart(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart.items.all().delete()
    request.session.pop(SESSION_KEY, None)
    messages.success(request, 'Cart cleared.')
    return redirect('cart_view')
