# Generated by Django 3.1.7 on 2021-03-17 13:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ota_app', '0010_auto_20210317_1255'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='guest',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='guest_reviews', to=settings.AUTH_USER_MODEL),
        ),
    ]
