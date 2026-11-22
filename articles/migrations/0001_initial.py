from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):
    initial = True
    dependencies = [('core', '0001_initial'), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel('Article', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
            ('title', models.CharField(max_length=200)),
            ('slug', models.SlugField(unique=True)),
            ('category', models.CharField(max_length=100)),
            ('content', models.TextField()),
            ('summary', models.CharField(max_length=300)),
            ('featured_image', models.ImageField(blank=True, null=True, upload_to='articles/')),
            ('views', models.IntegerField(default=0)),
            ('is_published', models.BooleanField(default=True)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='articles', to=settings.AUTH_USER_MODEL)),
            ('recommended_products', models.ManyToManyField(blank=True, related_name='articles', to='core.product')),
        ], options={'ordering': ['-created_at']}),
        migrations.CreateModel('UserHealthProfile', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
            ('age', models.IntegerField(blank=True, null=True)),
            ('gender', models.CharField(blank=True, max_length=20)),
            ('medical_conditions', models.TextField(blank=True)),
            ('allergies', models.TextField(blank=True)),
            ('updated_at', models.DateTimeField(auto_now=True)),
            ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='health_profile', to=settings.AUTH_USER_MODEL)),
        ]),
    ]
