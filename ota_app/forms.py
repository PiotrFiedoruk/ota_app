import django.forms as forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email, URLValidator


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