from django.db import models
from django.contrib.auth.models import User
from core.models import Product
import uuid

class Order(models.Model):
    STATUS_CHOICES = (('pending','Pending'),('processing','Processing'),('shipped','Shipped'),('delivered','Delivered'),('cancelled','Cancelled'))
    PAYMENT_STATUS = (('pending','Pending'),('paid','Paid'),('failed','Failed'),('refunded','Refunded'))
    PAYMENT_METHODS = (('cash','Cash on Delivery'),('simulated','Card Payment (Simulated)'),('easypaisa','Easypaisa / Card'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True, default='')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    payment_reference = models.CharField(max_length=100, blank=True, default='', help_text='Easypaisa transaction reference, when paid online.')
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta: ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f'MM-{uuid.uuid4().hex[:8].upper()}'
        super().save(*args, **kwargs)

    def __str__(self): return f'Order #{self.order_number}'

    @property
    def status_badge(self):
        return {'pending':'warning','processing':'info','shipped':'primary','delivered':'success','cancelled':'danger'}.get(self.status,'secondary')

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self): return f'{self.quantity} x {self.product.name}'
    def get_total(self): return self.quantity * self.price
