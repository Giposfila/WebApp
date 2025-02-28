# forms.py
from django import forms
from .models import UsersDB

class UsersForm(forms.ModelForm):
    class Meta:
        model = UsersDB
        fields = ['Email', 'Password']
        widget=[

        ]# Укажите поля, которые должны быть в форме