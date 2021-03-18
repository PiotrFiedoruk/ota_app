import django.forms as forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email, URLValidator
from ota_app.models import Hotel, Review
import datetime



# validators:

# example:
# def validate_even(value):
#   if value % 2 != 0:
#     raise ValidationError("{} nie jest parzyste!".format(value))


# how to use:
# class MyForm(forms.Form):
#   num = forms.IntegerField(label='wpisz parzystą liczbę',
#                            validators=[validate_even])

def validate_past_date(date):
    if date < datetime.date.today():
        raise ValidationError('date cannot be in the past')

def number_not_negative(number):
    if number < 0:
        raise ValidationError('this value has to be larger than 0')

def hotel_name_unique(name):
    if Hotel.objects.filter(name=name):
        raise ValidationError('hotel with this email already exists')

def email_unique(email):
    if User.objects.filter(email=email):
        raise ValidationError('user with this email already exists')

class AddReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['title', 'text', 'score_overall','score_location','score_cleaning','score_service']

class AddHotelForm(forms.Form):
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

    name = forms.CharField(max_length=64,validators=[hotel_name_unique])
    city = forms.CharField(max_length=64)
    street = forms.CharField(max_length=128)
    description = forms.CharField(max_length=3000, widget=forms.Textarea)
    facilities = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=FACILITIES)




class AddUserForm(forms.Form):
    username = forms.CharField(max_length=64, label='login')
    password = forms.CharField(max_length=64, widget=forms.PasswordInput, label='password')
    repeat_password = forms.CharField(max_length=64, widget=forms.PasswordInput, label='repeat password')
    first_name = forms.CharField(max_length=64, label='first name')
    last_name = forms.CharField(max_length=64, label='last surname')
    email = forms.EmailField(max_length=64, validators=[email_unique], label='email')

class LoginForm(forms.Form):
    login = forms.CharField(max_length=64, label='login')
    password = forms.CharField(max_length=64, widget=forms.PasswordInput, label='password')

class ResetPasswordForm(forms.Form):
    password = forms.CharField(max_length=64, widget=forms.PasswordInput, label='enter password')
    repeat_password = forms.CharField(max_length=64, widget=forms.PasswordInput, label='repeat password')

class AddRoomForm(forms.Form):
    name = forms.CharField(max_length=128)

class AddRateplanForm(forms.Form):
    name = forms.CharField(max_length=32)
    price_1 = forms.DecimalField(max_digits=7, decimal_places=2, validators=[number_not_negative])
    price_2 = forms.DecimalField(max_digits=7, decimal_places=2, validators=[number_not_negative])
