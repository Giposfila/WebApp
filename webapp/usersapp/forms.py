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


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}))

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email не найден")
        return email


class ResetPasswordForm(forms.Form):
    new_password1 = forms.CharField(
        label="Новый пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label="Подтвердите пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("new_password1")
        password2 = cleaned_data.get("new_password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return cleaned_data