from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth.models import User
from .models import *
class CreateBoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['title', 'description']  # Поля формы

        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'Введите название доски',
                'class': 'form-control'  # Добавляем класс для стилизации
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Введите описание доски',
                'rows': 4,  # Количество строк
                'class': 'form-control'  # Добавляем класс для стилизации
            }),
        }
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    def clean_title(self):
        """Проверка уникальности названия доски."""
        title = self.cleaned_data.get('title')
        if self.user and Board.objects.filter(title=title, created_by=self.user).exists():
            raise forms.ValidationError("Доска с таким названием уже существует.")
        return title
    def save(self, commit=True, user=None):
        instance = super().save(commit=False)
        if user:
            instance.created_by = user  # Присваиваем текущего пользователя
            instance.save()  # Сохраняем экземпляр перед добавлением участников
            instance.members.add(user)  # Добавляем текущего пользователя в участники
        if commit:
            instance.save()
        return instance