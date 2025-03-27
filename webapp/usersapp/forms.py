from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class UsersForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-input-register'}),
        validators=[
            RegexValidator(
                regex='^[\\w.@+-]+$',
                message='Имя пользователя может содержать только буквы, цифры и символы @/./+/-/_'
            )
        ]
    )
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-input-register'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input-register'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input-register'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input-login'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input-login'}))