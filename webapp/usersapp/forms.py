# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UsersForm(UserCreationForm):
    username= forms.CharField(widget=forms.TextInput(),label='Имя пользователя', help_text=None)
    password1 = forms.CharField(widget=forms.PasswordInput(), label='Пароль', help_text='Пароль должен содержать не менее 8 символов\n Пароль не может состоять лишь из цифр')
    password2 = forms.CharField(widget=forms.PasswordInput(), label='Повторите пароль')
    class Meta:
        model=User
        fields = ['username','email','password1','password2']
        def __init__(self):
            super().__init__()
            self.fields['password1'].help_text=None
            self.fields['password2'].help_text = None
            self.fields['password'].help_text = None
