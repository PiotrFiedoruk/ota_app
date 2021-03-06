# Generated by Django 3.1.7 on 2021-03-18 10:50

from django.db import migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('ota_app', '0013_auto_20210317_1517'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hotel',
            name='facilities',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('concierge-bell', 'Concierge'), ('utensils', 'Restaurant'), ('swimming-pool', 'Pool'), ('umbrella-beach', 'Beach'), ('shuttle-van', 'Shuttle'), ('skiing', 'Skiing'), ('wheelchair', 'Disabled facilities'), ('wifi', 'Wifi'), ('tv', 'TV'), ('cocktail', 'Bar'), ('snowflake', 'Air Conditioning'), ('parking', 'Parking'), ('smoking-ban', 'No smoking'), ('dumbbell', 'Gym')], max_length=138),
        ),
    ]
