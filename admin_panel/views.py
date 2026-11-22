from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from django.utils.text import slugify
from core.models import Product, Category, Prescription, HeroImage, PromotionalBanner, PromoImage, TeamMember
from orders.models import Order
from django.contrib.auth.models import User

def is_admin(user):
    return user.is_authenticated and (user.is_superuser or user.is_staff)

@login_required
@user_passes_test(is_admin)
def dashboard_home(request):
    total_products = Product.objects.filter(is_active=True).count()
    total_orders = Order.objects.count()
    total_users = User.objects.count()
    total_revenue = Order.objects.filter(payment_status='paid').aggregate(t=Sum('total_amount'))['t'] or 0
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:10]
    low_stock = Product.objects.filter(stock__lt=10, is_active=True).order_by('stock')[:10]
    pending_prescriptions = Prescription.objects.filter(status='pending').count()
    pending_orders = Order.objects.filter(status='pending').count()
    return render(request, 'admin_panel/dashboard.html', {
        'total_products': total_products, 'total_orders': total_orders,
        'total_users': total_users, 'total_revenue': total_revenue,
        'recent_orders': recent_orders, 'low_stock': low_stock,
        'pending_prescriptions': pending_prescriptions, 'pending_orders': pending_orders,
    })

@login_required
@user_passes_test(is_admin)
def product_management(request):
    q = request.GET.get('q','')
    products = Product.objects.select_related('category').order_by('-created_at')
    if q: products = products.filter(name__icontains=q)
    return render(request, 'admin_panel/product_management.html', {'products': products, 'q': q})

@login_required
@user_passes_test(is_admin)
def product_add(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name','').strip()
        category_id = request.POST.get('category')
        if not name or not category_id:
            messages.error(request, 'Name and category are required.')
        else:
            base_slug = slugify(name)
            slug = base_slug
            count = Product.objects.filter(slug__startswith=base_slug).count()
            if count: slug = f'{base_slug}-{count}'
            product = Product(
                name=name, slug=slug, category_id=category_id,
                price=request.POST.get('price',0), discount_price=request.POST.get('discount_price') or None,
                stock=request.POST.get('stock',0), description=request.POST.get('description',''),
                short_description=request.POST.get('short_description',''),
                manufacturer=request.POST.get('manufacturer',''),
                prescription_required=request.POST.get('prescription_required','not_required'),
                is_active=request.POST.get('is_active')=='on',
                is_featured=request.POST.get('is_featured')=='on',
            )
            if request.FILES.get('image'): product.image = request.FILES['image']
            if request.FILES.get('image_hover'): product.image_hover = request.FILES['image_hover']
            product.save()
            messages.success(request, f'Product "{name}" added!')
            return redirect('product_management')
    return render(request, 'admin_panel/product_form.html', {'categories': categories, 'action': 'Add'})

@login_required
@user_passes_test(is_admin)
def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()
    if request.method == 'POST':
        product.name = request.POST.get('name', product.name).strip()
        product.category_id = request.POST.get('category', product.category_id)
        product.price = request.POST.get('price', product.price)
        product.discount_price = request.POST.get('discount_price') or None
        product.stock = request.POST.get('stock', product.stock)
        product.description = request.POST.get('description', product.description)
        product.short_description = request.POST.get('short_description','')
        product.manufacturer = request.POST.get('manufacturer','')
        product.prescription_required = request.POST.get('prescription_required','not_required')
        product.is_active = request.POST.get('is_active')=='on'
        product.is_featured = request.POST.get('is_featured')=='on'
        if request.FILES.get('image'): product.image = request.FILES['image']
        if request.FILES.get('image_hover'): product.image_hover = request.FILES['image_hover']
        product.save()
        messages.success(request, f'Product "{product.name}" updated!')
        return redirect('product_management')
    return render(request, 'admin_panel/product_form.html', {'product': product, 'categories': categories, 'action': 'Edit'})

@login_required
@user_passes_test(is_admin)
def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        name = product.name; product.delete()
        messages.success(request, f'Product "{name}" deleted.')
        return redirect('product_management')
    return render(request, 'admin_panel/product_confirm_delete.html', {'product': product})

@login_required
@user_passes_test(is_admin)
def category_management(request):
    categories = Category.objects.annotate(product_count=Count('products'))
    if request.method == 'POST':
        name = request.POST.get('name','').strip()
        if name:
            Category.objects.get_or_create(name=name, defaults={'slug': slugify(name)})
            messages.success(request, f'Category "{name}" added!')
            return redirect('category_management')
    return render(request, 'admin_panel/category_management.html', {'categories': categories})

@login_required
@user_passes_test(is_admin)
def order_management(request):
    status_filter = request.GET.get('status','')
    orders = Order.objects.select_related('user').prefetch_related('items__product').order_by('-created_at')
    if status_filter: orders = orders.filter(status=status_filter)
    return render(request, 'admin_panel/order_management.html', {'orders': orders, 'status_filter': status_filter, 'status_choices': Order.STATUS_CHOICES})

@login_required
@user_passes_test(is_admin)
def order_update_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        order.status = request.POST.get('status', order.status)
        order.save(); messages.success(request, f'Order #{order.order_number} updated.')
    return redirect('order_management')

@login_required
@user_passes_test(is_admin)
def prescription_management(request):
    status_filter = request.GET.get('status','')
    prescriptions = Prescription.objects.select_related('user','product').order_by('-upload_date')
    if status_filter: prescriptions = prescriptions.filter(status=status_filter)
    return render(request, 'admin_panel/prescription_management.html', {'prescriptions': prescriptions, 'status_filter': status_filter})

@login_required
@user_passes_test(is_admin)
def prescription_review(request, rx_id):
    rx = get_object_or_404(Prescription, id=rx_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action in ('approved','rejected'):
            rx.status = action
            rx.review_notes = request.POST.get('review_notes','').strip()
            rx.reviewed_at = timezone.now()
            rx.reviewed_by = request.user
            rx.save()
            messages.success(request, f'Prescription #{rx.id} {action}.')
    return redirect('prescription_management')

@login_required
@user_passes_test(is_admin)
def user_management(request):
    users = User.objects.order_by('-date_joined')
    return render(request, 'admin_panel/user_management.html', {'users': users})

@login_required
@user_passes_test(is_admin)
def banner_management(request):
    q = request.GET.get('q','')
    banners = PromotionalBanner.objects.order_by('order','-created_at')
    if q: banners = banners.filter(title__icontains=q)
    return render(request, 'admin_panel/banner_management.html', {'banners': banners, 'q': q})

@login_required
@user_passes_test(is_admin)
def banner_add(request):
    if request.method == 'POST':
        banner = PromotionalBanner(
            title=request.POST.get('title',''), subtitle=request.POST.get('subtitle',''),
            background_color=request.POST.get('background_color','#1565c0'),
            text_color=request.POST.get('text_color','#ffffff'),
            button_text=request.POST.get('button_text',''), button_link=request.POST.get('button_link',''),
            banner_type=request.POST.get('banner_type','home_full'),
            is_active=request.POST.get('is_active')=='on', order=request.POST.get('order',0),
            start_date=request.POST.get('start_date') or None, end_date=request.POST.get('end_date') or None,
        )
        if request.FILES.get('image'): banner.image = request.FILES['image']
        banner.save(); messages.success(request, 'Banner created!')
        return redirect('banner_management')
    return render(request, 'admin_panel/banner_form.html', {'action':'Add','banner_types':PromotionalBanner.BANNER_TYPES})

@login_required
@user_passes_test(is_admin)
def banner_edit(request, banner_id):
    banner = get_object_or_404(PromotionalBanner, id=banner_id)
    if request.method == 'POST':
        banner.title=request.POST.get('title',banner.title); banner.subtitle=request.POST.get('subtitle','')
        banner.background_color=request.POST.get('background_color',banner.background_color)
        banner.text_color=request.POST.get('text_color',banner.text_color)
        banner.button_text=request.POST.get('button_text',''); banner.button_link=request.POST.get('button_link','')
        banner.banner_type=request.POST.get('banner_type',banner.banner_type)
        banner.is_active=request.POST.get('is_active')=='on'; banner.order=request.POST.get('order',banner.order)
        banner.start_date=request.POST.get('start_date') or None; banner.end_date=request.POST.get('end_date') or None
        if request.FILES.get('image'): banner.image=request.FILES['image']
        banner.save(); messages.success(request, 'Banner updated!')
        return redirect('banner_management')
    return render(request, 'admin_panel/banner_form.html', {'banner':banner,'action':'Edit','banner_types':PromotionalBanner.BANNER_TYPES})

@login_required
@user_passes_test(is_admin)
def banner_delete(request, banner_id):
    banner = get_object_or_404(PromotionalBanner, id=banner_id)
    if request.method == 'POST':
        banner.delete(); messages.success(request, 'Banner deleted.')
        return redirect('banner_management')
    return render(request, 'admin_panel/confirm_delete.html', {'item': banner, 'item_name': banner.title, 'back_url': 'banner_management'})

@login_required
@user_passes_test(is_admin)
def banner_toggle(request, banner_id):
    banner = get_object_or_404(PromotionalBanner, id=banner_id)
    banner.is_active = not banner.is_active; banner.save()
    messages.success(request, f'Banner {"activated" if banner.is_active else "deactivated"}.')
    return redirect('banner_management')

# ── Promotional Images ─────────────────────────────────────────────────────
@login_required
@user_passes_test(is_admin)
def promo_management(request):
    promos = PromoImage.objects.order_by('order','-created_at')
    return render(request, 'admin_panel/promo_management.html', {'promos': promos})

@login_required
@user_passes_test(is_admin)
def promo_add(request):
    if request.method == 'POST':
        if not request.POST.get('title','').strip() or not request.FILES.get('image'):
            messages.error(request, 'Title and image are required.')
        else:
            promo = PromoImage(
                title=request.POST.get('title','').strip(),
                subtitle=request.POST.get('subtitle',''),
                badge_text=request.POST.get('badge_text',''),
                button_text=request.POST.get('button_text','Shop Now'),
                button_link=request.POST.get('button_link','/products/'),
                position=request.POST.get('position','full'),
                overlay_color=request.POST.get('overlay_color','rgba(13,71,161,0.55)'),
                text_color=request.POST.get('text_color','#ffffff'),
                order=request.POST.get('order',0),
                is_active=request.POST.get('is_active')=='on',
                start_date=request.POST.get('start_date') or None,
                end_date=request.POST.get('end_date') or None,
                image=request.FILES['image'],
            )
            promo.save()
            messages.success(request, f'Promotional image "{promo.title}" added!')
            return redirect('promo_management')
    return render(request, 'admin_panel/promo_form.html', {'action':'Add','position_choices':PromoImage.POSITION_CHOICES})

@login_required
@user_passes_test(is_admin)
def promo_edit(request, promo_id):
    promo = get_object_or_404(PromoImage, id=promo_id)
    if request.method == 'POST':
        promo.title=request.POST.get('title',promo.title).strip()
        promo.subtitle=request.POST.get('subtitle','')
        promo.badge_text=request.POST.get('badge_text','')
        promo.button_text=request.POST.get('button_text','Shop Now')
        promo.button_link=request.POST.get('button_link','/products/')
        promo.position=request.POST.get('position',promo.position)
        promo.overlay_color=request.POST.get('overlay_color',promo.overlay_color)
        promo.text_color=request.POST.get('text_color',promo.text_color)
        promo.order=request.POST.get('order',promo.order)
        promo.is_active=request.POST.get('is_active')=='on'
        promo.start_date=request.POST.get('start_date') or None
        promo.end_date=request.POST.get('end_date') or None
        if request.FILES.get('image'): promo.image=request.FILES['image']
        promo.save()
        messages.success(request, 'Promotional image updated!')
        return redirect('promo_management')
    return render(request, 'admin_panel/promo_form.html', {'promo':promo,'action':'Edit','position_choices':PromoImage.POSITION_CHOICES})

@login_required
@user_passes_test(is_admin)
def promo_delete(request, promo_id):
    promo = get_object_or_404(PromoImage, id=promo_id)
    if request.method == 'POST':
        promo.delete(); messages.success(request, 'Promotional image deleted.')
        return redirect('promo_management')
    return render(request, 'admin_panel/confirm_delete.html', {'item':promo,'item_name':promo.title,'back_url':'promo_management'})

@login_required
@user_passes_test(is_admin)
def promo_toggle(request, promo_id):
    promo = get_object_or_404(PromoImage, id=promo_id)
    promo.is_active = not promo.is_active; promo.save()
    messages.success(request, f'Promo image {"activated" if promo.is_active else "deactivated"}.')
    return redirect('promo_management')
