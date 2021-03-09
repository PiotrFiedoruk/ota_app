from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Hotel_owner(models.Model):
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    email = models.EmailField(unique=True)

class Hotel(models.Model):
    name = models.CharField(max_length=64)
    city = models.CharField(max_length=64)
    # hotel_owner = models.ForeignKey(Hotel_owner, on_delete=models.CASCADE, related_name='hotels_owned', default=1) to add later
    def __str__(self):
        return self.name

class Room(models.Model):
    hotel_id = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='hotel_rooms')
    name = models.CharField(max_length=64)
    def __str__(self):
        return self.name

class Rateplan(models.Model):
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='room_rateplans')
    name = models.CharField(max_length=64)
    def __str__(self):
        return self.name

class Price(models.Model):
    rateplan_id = models.ForeignKey(Rateplan, on_delete=models.CASCADE, related_name='rateplan_prices')
    date = models.DateField()
    price_1 = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    price_2 = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    availability = models.SmallIntegerField()

    class Meta:
        ordering = ["date"]

class Guest(models.Model):
    guest = models.OneToOneField(User, on_delete=models.CASCADE)

class HotelOwner(models.Model):
    hotel_owner = models.OneToOneField(User, on_delete=models.CASCADE)

class Reservation(models.Model):
    guest_id = models.ForeignKey(Guest, on_delete=models.PROTECT)
    price_id = models.ManyToManyField(Room)


# https://docs.djangoproject.com/en/dev/topics/db/queries/#field-lookups

# Hotel.objects.filter(city='Beirut',room__rateplan__prices__availability=1)

# From stack overflow
# Hotel.objects.filter(
#     city=your_city,
#     room__rateplan__prices__date=your_date,
#     room__rateplan__prices__price_1=your_price,
#     room__rateplan__prices__availability=your_availability,
# ).distinct()

# Works! vvvv
# Hotel.objects.filter(
#     city='Warsaw',
#     room__rateplan__prices__date__range=['2021-01-01', '2021-12-30'],
#     room__rateplan__prices__availability=1,
# ).distinct()

# Works with price too:
# hotelsearch = Hotel.objects.filter(
#     city='Warsaw',
#     room__rateplan__prices__date__range=['2021-01-01', '2021-12-30'],
#     room__rateplan__prices__price_1__isnull=False,
#     room__rateplan__prices__availability__gt=0,
# ).distinct()

# you can iterate through results:
# for h in hotelsearch:
#     print(h.name)
