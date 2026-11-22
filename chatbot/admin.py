from django.contrib import admin
from .models import ChatMessage, FAQ

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question','keywords','is_active','order')
    list_editable = ('is_active','order')

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user','session_id','is_user','timestamp')
    list_filter = ('is_user',)
