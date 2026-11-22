from django.contrib import admin
from .models import Article, UserHealthProfile

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title','author','category','is_published','views','created_at')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(UserHealthProfile)
class HealthProfileAdmin(admin.ModelAdmin):
    list_display = ('user','age','gender','updated_at')
