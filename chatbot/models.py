from django.db import models
from django.contrib.auth.models import User

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    message = models.TextField(blank=True, default='')
    response = models.TextField(blank=True, default='')
    is_user = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['timestamp']
    def __str__(self): return f"{'User' if self.is_user else 'Bot'} @ {self.timestamp:%Y-%m-%d %H:%M}"

class FAQ(models.Model):
    question = models.CharField(max_length=300)
    answer = models.TextField()
    keywords = models.CharField(max_length=500, help_text='Comma-separated keywords')
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    class Meta: ordering = ['order','question']
    def __str__(self): return self.question
