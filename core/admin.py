from django.contrib import admin
from .models import Category, Product, Prescription, HeroImage, PromotionalBanner, PromoImage, TeamMember

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'prescription_required', 'is_active', 'is_featured')
    list_filter = ('category', 'is_active', 'is_featured', 'prescription_required')
    search_fields = ('name', 'generic_name')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'is_featured', 'stock')

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'status', 'upload_date')
    list_filter = ('status',)
    list_editable = ('status',)

@admin.register(HeroImage)
class HeroImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_editable = ('order', 'is_active')

@admin.register(PromoImage)
class PromoImageAdmin(admin.ModelAdmin):
    list_display = ('title', 'position', 'order', 'is_active', 'start_date', 'end_date')
    list_editable = ('order', 'is_active')
    list_filter = ('position', 'is_active')

@admin.register(PromotionalBanner)
class PromotionalBannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'banner_type', 'is_active', 'order')
    list_editable = ('is_active', 'order')

@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'order', 'is_active')
    list_editable = ('order', 'is_active')
