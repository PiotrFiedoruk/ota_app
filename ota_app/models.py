from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from multiselectfield import MultiSelectField


class Hotel_owner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


FACILITIES = (("Concierge", "Concierge"),
              ("Restaurant", "Restaurant"),
              ("Swimming Pool", "Swimming Pool"),
              ("Beach", "Beach"),
              ("Shuttle", "Shuttle"),
              ("Skiing", "Skiing"),
              ("Disabled facilities", "Disabled facilities"),
              ("Wifi", "Wifi"),
              ("TV", "TV"),
              ("Bar", "Bar"),
              ("Air Conditioning", "Air Conditioning"),
              ("Parking", "Parking"),
              ("No smoking", "No smoking"),
              ("Gym", "Gym"))

AMENITIES = (("Disabled facilities", "Disabled facilities"),
              ("Wifi", "Wifi"),
              ("TV", "TV"),
              ("Air Conditioning", "Air Conditioning"),
              ("Shower", "Shower"),
              ("Bath", "Bath"),
              ("Tea/Coffee", "Tea/Coffee"),
              ("No smoking", "No smoking"))


class Hotel(models.Model):
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
    description = models.TextField(max_length=1200)
    amenities = MultiSelectField(choices=AMENITIES)

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
    hotel = models.ForeignKey(Hotel, on_delete=models.PROTECT, related_name='hotel_reservations')
    guest = models.ForeignKey(User, on_delete=models.PROTECT, related_name='guest_reservations')
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name='guest_reservations')
    rateplan = models.ManyToManyField(Rateplan)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    arrival = models.DateField()
    departure = models.DateField()
    num_of_guests = models.SmallIntegerField()
    status = models.CharField(choices=RESERVATION_STATUS, max_length=12)
    created = models.DateTimeField(auto_now_add=True)


class Review(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='hotel_reviews')
    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name='guest_reviews')
    title = models.CharField(max_length=256)
    text = models.TextField(max_length=3000)
    score_overall = models.SmallIntegerField(validators=[MaxValueValidator(10), MinValueValidator(1)])
    score_location = models.SmallIntegerField(validators=[MaxValueValidator(10), MinValueValidator(1)])
    score_cleaning = models.SmallIntegerField(validators=[MaxValueValidator(10), MinValueValidator(1)])
    score_service = models.SmallIntegerField(validators=[MaxValueValidator(10), MinValueValidator(1)])
    created = models.DateTimeField(auto_now_add=True)


# class Message(models.Model):
#     subject = models.CharField(max_length=256, verbose_name='Subject')
#     content = models.TextField()
#     message_to = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='do:')
#     message_from = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='od:')
#     date_sent = models.DateTimeField(auto_now=True)