from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, default='fa-pills')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    PRESCRIPTION_CHOICES = [
        ('not_required', 'No Prescription Needed'),
        ('required', 'Prescription Required'),
        ('optional', 'Prescription Optional'),
    ]
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    generic_name = models.CharField(max_length=200, blank=True)
    manufacturer = models.CharField(max_length=200, default='Unknown')
    description = models.TextField(default='')
    short_description = models.CharField(max_length=300, default='')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.IntegerField(default=0)
    prescription_required = models.CharField(max_length=20, choices=PRESCRIPTION_CHOICES, default='not_required')
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    image_hover = models.ImageField(upload_to='products/hover/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def final_price(self):
        return self.discount_price if self.discount_price else self.price

    @property
    def discount_percent(self):
        if self.discount_price and self.price > 0:
            return int(((self.price - self.discount_price) / self.price) * 100)
        return 0

    @property
    def needs_prescription(self):
        return self.prescription_required == 'required'

    @property
    def in_stock(self):
        return self.stock > 0


class Prescription(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prescriptions')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='prescriptions')
    prescription_image = models.ImageField(upload_to='prescriptions/')
    doctor_name = models.CharField(max_length=200, blank=True, default='')
    patient_name = models.CharField(max_length=200, blank=True, default='')
    notes = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    review_notes = models.TextField(blank=True, default='')
    upload_date = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_prescriptions')

    class Meta:
        ordering = ['-upload_date']

    def __str__(self):
        return f"Rx #{self.id} - {self.user.username} ({self.status})"

    @property
    def is_approved(self):
        return self.status == 'approved'

    @property
    def status_badge(self):
        return {'pending': 'warning', 'approved': 'success', 'rejected': 'danger', 'expired': 'secondary'}.get(self.status, 'secondary')


class HeroImage(models.Model):
    title = models.CharField(max_length=200, blank=True)
    subtitle = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='hero/')
    button_text = models.CharField(max_length=50, blank=True, default='Shop Now')
    button_link = models.CharField(max_length=200, blank=True, default='/products/')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title or f"Hero Image {self.id}"


class PromoImage(models.Model):
    """Promotional images displayed on homepage — manageable from admin dashboard."""
    POSITION_CHOICES = [
        ('full', 'Full Width Banner'),
        ('half_left', 'Half Width — Left'),
        ('half_right', 'Half Width — Right'),
        ('third', 'One Third Width'),
    ]
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    badge_text = models.CharField(max_length=60, blank=True, help_text='Small badge e.g. "NEW" or "SALE"')
    image = models.ImageField(upload_to='promo/', help_text='Recommended: 1200×500px for full, 600×500px for half')
    button_text = models.CharField(max_length=60, blank=True, default='Shop Now')
    button_link = models.CharField(max_length=200, blank=True, default='/products/')
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, default='full')
    overlay_color = models.CharField(max_length=30, blank=True, default='rgba(13,71,161,0.55)', help_text='CSS rgba overlay')
    text_color = models.CharField(max_length=20, blank=True, default='#ffffff')
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_position_display()})"


class PromotionalBanner(models.Model):
    BANNER_TYPES = [
        ('top_bar', 'Top Announcement Bar'),
        ('home_full', 'Homepage Full Width'),
        ('home_side', 'Homepage Sidebar'),
        ('product_page', 'Product Page'),
    ]
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='banners/', blank=True, null=True)
    background_color = models.CharField(max_length=30, blank=True, default='#1565c0')
    text_color = models.CharField(max_length=20, blank=True, default='#ffffff')
    button_text = models.CharField(max_length=50, blank=True)
    button_link = models.CharField(max_length=200, blank=True)
    banner_type = models.CharField(max_length=20, choices=BANNER_TYPES, default='home_full')
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_banner_type_display()})"


class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    image = models.ImageField(upload_to='team/', blank=True, null=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name
