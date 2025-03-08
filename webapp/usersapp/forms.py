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
from django import forms
from django.contrib.auth import authenticate

class LoginForm(forms.Form):
    username = forms.CharField(
        label="Имя пользователя",
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            # Проверяем, существует ли пользователь с таким именем и паролем
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("Неверное имя пользователя или пароль")
            elif not user.is_active:
                raise forms.ValidationError("Пользователь не активен")
            else:
                # Сохраняем пользователя в cleaned_data для дальнейшего использования
                cleaned_data['user'] = user
        return cleaned_data