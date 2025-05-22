# forms.py
from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth import authenticate
from django.db.models import Q  # Добавляем этот импорт


class UsersForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(), label='Имя пользователя', help_text=None)
    email = forms.EmailField(required=True, label='Email')
    password1 = forms.CharField(widget=forms.PasswordInput(), label='Пароль',
                                help_text='Пароль должен содержать не менее 8 символов\n Пароль не может состоять лишь из цифр')
    password2 = forms.CharField(widget=forms.PasswordInput(), label='Повторите пароль')
    captcha = CaptchaField(label='Введите текст с картинки')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'captcha']
        def __init__(self):
            super().__init__()
            self.fields['password1'].help_text=None
            self.fields['password2'].help_text = None
            self.fields['password'].help_text = None


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Логин / Email",
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    captcha = CaptchaField(label='Введите текст с картинки')

    def clean(self):
        cleaned_data = super().clean()
        username_or_email = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username_or_email and password:
            try:
                user = User.objects.get(Q(username=username_or_email) | Q(email=username_or_email))
                if not user.check_password(password):
                    raise forms.ValidationError("Неверный пароль")
                elif not user.is_active:
                    raise forms.ValidationError("Пользователь не активен")
                self.cleaned_data['user'] = user
            except User.DoesNotExist:
                raise forms.ValidationError("Пользователь не найден")
        return cleaned_data

class ChangeUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']  # Логин и Email

class ProfileForm(forms.ModelForm):
    avatar = forms.ImageField(
        label="Фото профиля",  # Изменяем метку здесь
        required=False
    )
    class Meta:
        model = Profile
        fields = ['avatar']


class EmailConfirmationForm(forms.Form):
    code = forms.CharField(
        label="Код подтверждения",
        max_length=6,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )