from django.urls import path
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('products/', views.products_list, name='products_list'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('upload-prescription/', views.upload_prescription, name='upload_prescription'),
    path('my-prescriptions/', views.my_prescriptions, name='my_prescriptions'),
]
