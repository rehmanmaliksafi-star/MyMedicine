from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('easypaisa/start/<int:order_id>/', views.easypaisa_start, name='easypaisa_start'),
    path('easypaisa/simulate/<int:order_id>/', views.easypaisa_simulate, name='easypaisa_simulate'),
    path('easypaisa/callback/', views.easypaisa_callback, name='easypaisa_callback'),
]
