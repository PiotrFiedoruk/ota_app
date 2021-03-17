# Generated by Django 3.1.7 on 2021-03-17 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ota_app', '0008_reservation_room'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='status',
            field=models.CharField(choices=[('ACT', 'Active'), ('CLX', 'Cancelled')], default='ACT', max_length=12),
            preserve_default=False,
        ),
    ]