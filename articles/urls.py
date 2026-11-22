from django.urls import path
from . import views
urlpatterns = [
    path('', views.article_list, name='article_list'),
    path('health-profile/', views.health_profile, name='health_profile'),
    path('<slug:slug>/', views.article_detail, name='article_detail'),
]
