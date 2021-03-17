import django.forms as forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email, URLValidator
from ota_app.models import Hotel
import datetime


def hotel_name_unique(name):
    if Hotel.objects.filter(name=name):
        raise ValidationError('hotel with this email already exists')

class AddHotelForm(forms.Form):
    name = forms.CharField(max_length=64,validators=[hotel_name_unique])
    city = forms.CharField(max_length=64)

def email_unique(email):
    if User.objects.filter(email=email):
        raise ValidationError('user with this email already exists')

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


def validate_past_date(date):
    if date < datetime.date.today():
        raise ValidationError('date cannot be in the past')

def number_not_negative(number):
    if number < 0:
        raise ValidationError('this value has to be larger than 0')

class AddRateplanForm(forms.Form):
    name = forms.CharField(max_length=32)
    price_1 = forms.DecimalField(max_digits=7, decimal_places=2)
    price_2 = forms.DecimalField(max_digits=7, decimal_places=2)
