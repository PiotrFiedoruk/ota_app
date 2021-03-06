# Generated by Django 3.1.7 on 2021-03-19 21:19

from django.db import migrations, models
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ota_app', '0014_auto_20210318_1050'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='amenities',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('Disabled facilities', 'Disabled facilities'), ('Wifi', 'Wifi'), ('TV', 'TV'), ('Air Conditioning', 'Air Conditioning'), ('Shower', 'Shower'), ('Bath', 'Bath'), ('Tea/Coffee', 'Tea/Coffee'), ('No smoking', 'No smoking')], default=1, max_length=78),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='room',
            name='description',
            field=models.TextField(default='some descritpion here', max_length=1200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='hotel',
            name='facilities',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('Concierge', 'Concierge'), ('Restaurant', 'Restaurant'), ('Swimming Pool', 'Swimming Pool'), ('Beach', 'Beach'), ('Shuttle', 'Shuttle'), ('Skiing', 'Skiing'), ('Disabled facilities', 'Disabled facilities'), ('Wifi', 'Wifi'), ('TV', 'TV'), ('Bar', 'Bar'), ('Air Conditioning', 'Air Conditioning'), ('Parking', 'Parking'), ('No smoking', 'No smoking'), ('Gym', 'Gym')], max_length=127),
        ),
    ]
