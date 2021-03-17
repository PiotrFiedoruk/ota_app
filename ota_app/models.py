from django.contrib.auth.models import User
from django.db import models
from multiselectfield import MultiSelectField

# Create your models here.

class Hotel_owner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Hotel(models.Model):
    FACILITIES = (("concierge-bell", "Concierge"),
                  ("utensils", "Restaurant" ),
                  ("swimming-pool", "Pool"),
                  ("umbrella-beach", "Beach"),
                  ("shuttle-van", "Shuttle"),
                  ("skiing", "Skiing"),
                  ("wheelchair", "Disabled faclities"),
                  ("wifi", "Wifi"),
                  ("tv", "TV"),
                  ("cocktail", "Bar"),
                  ("snowflake", "Air Conditioning"),
                  ("parking", "Parking"),
                  ("smoking-ban", "No smoking"),
                  ("dumbbell", "Gym"))
    hotel_owner = models.ForeignKey(Hotel_owner, on_delete=models.CASCADE, related_name='hotels_owned')
    name = models.CharField(max_length=64)
    city = models.CharField(max_length=64)
    street = models.CharField(max_length=128)
    description = models.TextField(max_length=1200)
    facilities = MultiSelectField(choices=FACILITIES)
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

class Reservation(models.Model):
    RESERVATION_STATUS = (('Act', 'Active'), ('CLX', 'Cancelled'))
    hotel =models.ForeignKey(Hotel, on_delete=models.PROTECT, related_name='hotel_reservations')
    guest = models.ForeignKey(User, on_delete=models.PROTECT, related_name='guest_reservations')
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name='guest_reservations')
    rateplan = models.ManyToManyField(Rateplan)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    arrival = models.DateField()
    departure= models.DateField()
    num_of_guests = models.SmallIntegerField()
    status = models.CharField(choices=RESERVATION_STATUS, max_length=12)
    created= models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='hotel_reviews')
    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name='guest_reviews')
    title = models.CharField(max_length=256)
    text = models.TextField(max_length=3000)
    score_overall = models.SmallIntegerField()
    score_location = models.SmallIntegerField()
    score_cleaning = models.SmallIntegerField()
    score_service = models.SmallIntegerField()
    created = models.DateTimeField(auto_now_add=True)





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
