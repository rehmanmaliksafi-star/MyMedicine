from django.conf import settings

def cart_count(request):
    count = 0
    if request.user.is_authenticated:
        try:
            from cart.models import Cart
            cart = Cart.objects.filter(user=request.user).first()
            if cart:
                count = cart.get_item_count()
        except Exception:
            pass
    return {'cart_count': count}

def site_settings(request):
    return {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'MyMedicine'),
        'SITE_TAGLINE': getattr(settings, 'SITE_TAGLINE', 'Your Trusted Online Pharmacy'),
        'SITE_EMAIL': getattr(settings, 'SITE_EMAIL', 'support@mymedicine.pk'),
        'SITE_PHONE': getattr(settings, 'SITE_PHONE', '0800-MYMED-RX'),
    }
