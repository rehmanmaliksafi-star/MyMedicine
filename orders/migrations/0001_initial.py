from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):
    initial = True
    dependencies = [('core', '0001_initial'), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel('Order', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
            ('order_number', models.CharField(editable=False, max_length=20, unique=True)),
            ('full_name', models.CharField(max_length=200)),
            ('email', models.EmailField()),
            ('phone', models.CharField(max_length=20)),
            ('address', models.TextField()),
            ('city', models.CharField(max_length=100)),
            ('postal_code', models.CharField(blank=True, default='', max_length=20)),
            ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
            ('status', models.CharField(choices=[('pending','Pending'),('processing','Processing'),('shipped','Shipped'),('delivered','Delivered'),('cancelled','Cancelled')], default='pending', max_length=20)),
            ('payment_status', models.CharField(choices=[('pending','Pending'),('paid','Paid'),('failed','Failed'),('refunded','Refunded')], default='pending', max_length=20)),
            ('payment_method', models.CharField(choices=[('cash','Cash on Delivery'),('simulated','Card Payment (Simulated)')], default='cash', max_length=20)),
            ('notes', models.TextField(blank=True, default='')),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('updated_at', models.DateTimeField(auto_now=True)),
            ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL)),
        ], options={'ordering': ['-created_at']}),
        migrations.CreateModel('OrderItem', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
            ('quantity', models.IntegerField()),
            ('price', models.DecimalField(decimal_places=2, max_digits=10)),
            ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='orders.order')),
            ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.product')),
        ]),
    ]
