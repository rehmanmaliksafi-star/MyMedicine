from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel('FAQ', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
            ('question', models.CharField(max_length=300)),
            ('answer', models.TextField()),
            ('keywords', models.CharField(max_length=500)),
            ('is_active', models.BooleanField(default=True)),
            ('order', models.IntegerField(default=0)),
        ], options={'ordering': ['order', 'question']}),
        migrations.CreateModel('ChatMessage', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
            ('session_id', models.CharField(blank=True, max_length=100)),
            ('message', models.TextField(blank=True, default='')),
            ('response', models.TextField(blank=True, default='')),
            ('is_user', models.BooleanField(default=True)),
            ('timestamp', models.DateTimeField(auto_now_add=True)),
            ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
        ], options={'ordering': ['timestamp']}),
    ]
