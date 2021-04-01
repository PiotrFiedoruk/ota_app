# Generated by Django 3.1.7 on 2021-03-11 12:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ota_app', '0003_remove_hotel_hotel_owner'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reservation',
            name='guest_id',
        ),
        migrations.RemoveField(
            model_name='reservation',
            name='price_id',
        ),
        migrations.AddField(
            model_name='reservation',
            name='arrival',
            field=models.DateField(default='2021-03-13'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reservation',
            name='departure',
            field=models.DateField(default='2021-03-15'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reservation',
            name='guest',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='auth.user'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reservation',
            name='hotel',
            field=models.ForeignKey(default=2, on_delete=django.db.models.deletion.PROTECT, to='ota_app.hotel'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reservation',
            name='num_of_guests',
            field=models.SmallIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reservation',
            name='price',
            field=models.DecimalField(decimal_places=2, default=12, max_digits=7),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reservation',
            name='rateplan',
            field=models.ManyToManyField(to='ota_app.Rateplan'),
        ),
        migrations.DeleteModel(
            name='Guest',
        ),
    ]