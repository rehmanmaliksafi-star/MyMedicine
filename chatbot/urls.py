from django.urls import path
from . import views
urlpatterns = [
    path('', views.chatbot_widget, name='chatbot_widget'),
    path('api/', views.chatbot_api, name='chatbot_api'),
]
