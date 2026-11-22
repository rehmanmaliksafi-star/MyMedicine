from django.db import models
from django.contrib.auth.models import User
from core.models import Product

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"Cart of {self.user.username}"
    def get_total(self): return sum(item.get_total() for item in self.items.select_related('product').all())
    def get_item_count(self): return sum(item.quantity for item in self.items.all())
    def is_empty(self): return not self.items.exists()

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    class Meta: unique_together = ('cart', 'product')
    def __str__(self): return f"{self.quantity} x {self.product.name}"
    def get_total(self): return self.product.final_price * self.quantity
