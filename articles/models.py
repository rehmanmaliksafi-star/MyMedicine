from django.db import models
from django.contrib.auth.models import User
from core.models import Product

class Article(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    category = models.CharField(max_length=100)
    content = models.TextField()
    summary = models.CharField(max_length=300)
    featured_image = models.ImageField(upload_to='articles/', blank=True, null=True)
    recommended_products = models.ManyToManyField(Product, blank=True, related_name='articles')
    views = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-created_at']
    def __str__(self): return self.title
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class UserHealthProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='health_profile')
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    medical_conditions = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return f"Health Profile - {self.user.username}"
