from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Prescription, Product, TeamMember, HeroImage, PromotionalBanner, Category, PromoImage


def home(request):
    featured_products = Product.objects.filter(is_active=True, is_featured=True).select_related('category')[:8]
    hero_images = HeroImage.objects.filter(is_active=True).order_by('order')
    categories = Category.objects.all()[:8]
    today = timezone.now().date()

    promo_images = PromoImage.objects.filter(
        is_active=True
    ).filter(
        Q(start_date__isnull=True) | Q(start_date__lte=today)
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=today)
    ).order_by('order')

    banners = PromotionalBanner.objects.filter(
        is_active=True, banner_type='home_full'
    ).filter(
        Q(start_date__isnull=True) | Q(start_date__lte=today)
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=today)
    ).order_by('order')[:2]

    top_bar = PromotionalBanner.objects.filter(
        is_active=True, banner_type='top_bar'
    ).filter(
        Q(start_date__isnull=True) | Q(start_date__lte=today)
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=today)
    ).first()

    return render(request, 'core/home.html', {
        'featured_products': featured_products,
        'hero_images': hero_images,
        'categories': categories,
        'promo_images': promo_images,
        'banners': banners,
        'top_bar': top_bar,
    })


def about(request):
    team_members = TeamMember.objects.filter(is_active=True).order_by('order')
    return render(request, 'core/about.html', {'team_members': team_members})


def products_list(request):
    products = Product.objects.filter(is_active=True).select_related('category')
    categories = Category.objects.all()
    category_slug = request.GET.get('category', '').strip()
    search_query = request.GET.get('q', '').strip()
    sort_by = request.GET.get('sort', 'newest')
    rx_filter = request.GET.get('rx', '')

    if category_slug:
        products = products.filter(category__slug=category_slug)
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | Q(generic_name__icontains=search_query) | Q(description__icontains=search_query)
        )
    if rx_filter == '1':
        products = products.filter(prescription_required='not_required')

    SORT = {'price_asc': 'price', 'price_desc': '-price', 'name_asc': 'name', 'newest': '-created_at'}
    products = products.order_by(SORT.get(sort_by, '-created_at'))

    return render(request, 'products/list.html', {
        'products': products, 'categories': categories,
        'current_category': category_slug, 'search_query': search_query, 'sort_by': sort_by,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(id=product.id)[:4]
    user_has_prescription = False
    if request.user.is_authenticated and product.needs_prescription:
        user_has_prescription = Prescription.objects.filter(user=request.user, product=product, status='approved').exists()
    return render(request, 'products/product_detail.html', {
        'product': product, 'related_products': related, 'user_has_prescription': user_has_prescription,
    })


@login_required
def upload_prescription(request):
    product_id = request.GET.get('product_id') or request.POST.get('product_id')
    product = None
    if product_id:
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            pass

    if request.method == 'POST':
        prescription_image = request.FILES.get('prescription_image')
        if not prescription_image:
            messages.error(request, 'Please upload a prescription image or PDF.')
        else:
            rx = Prescription.objects.create(
                user=request.user, product=product,
                doctor_name=request.POST.get('doctor_name', '').strip(),
                patient_name=request.POST.get('patient_name', '').strip() or request.user.get_full_name(),
                notes=request.POST.get('notes', '').strip(),
                prescription_image=prescription_image,
            )
            messages.success(request, f'Prescription #{rx.id} uploaded! Pharmacist will review within 24 hours.')
            return redirect('my_prescriptions')

    rx_products = Product.objects.filter(prescription_required='required', is_active=True)
    return render(request, 'core/upload_prescription.html', {'product': product, 'rx_products': rx_products})


@login_required
def my_prescriptions(request):
    prescriptions = Prescription.objects.filter(user=request.user).select_related('product').order_by('-upload_date')
    return render(request, 'core/my_prescriptions.html', {'prescriptions': prescriptions})
