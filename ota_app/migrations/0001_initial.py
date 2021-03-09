# Generated by Django 3.1.7 on 2021-03-07 23:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Guest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=64)),
                ('last_name', models.CharField(max_length=64)),
                ('email', models.EmailField(max_length=128, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Hotel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('city', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='Hotel_owner',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=64)),
                ('last_name', models.CharField(max_length=64)),
                ('email', models.EmailField(max_length=254, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('price_1', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True)),
                ('price_2', models.DecimalField(blank=True, decimal_places=2, max_digits=7, null=True)),
                ('availability', models.SmallIntegerField()),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('hotel_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hotel_rooms', to='ota_app.hotel')),
            ],
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guest_id', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ota_app.guest')),
                ('price_id', models.ManyToManyField(to='ota_app.Price')),
            ],
        ),
        migrations.CreateModel(
            name='Rateplan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('room_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='room_rateplans', to='ota_app.room')),
            ],
        ),
        migrations.AddField(
            model_name='price',
            name='rateplan_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rateplan_prices', to='ota_app.rateplan'),
        ),
        migrations.AddField(
            model_name='hotel',
            name='hotel_owner',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='hotels_owned', to='ota_app.hotel_owner'),
        ),
    ]
