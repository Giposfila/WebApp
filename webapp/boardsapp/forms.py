from django import forms
import datetime
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

class CreateTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'deadline', 'created_to']  # Поля формы

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
            'deadline': forms.DateTimeInput(
                attrs={
                    'placeholder': 'Выберите дату и время',
                    'type': 'datetime-local',  # активирует нативный календарь браузера
                    'class': 'form-control',  # для стилизации через Bootstrap
                    'required': False,  # обязательное поле
                    'autocomplete': 'off',  # отключает автозаполнение
                    'style': 'max-width: 300px;',  # ограничение ширины
                    'min': datetime.datetime.now().strftime('%Y-%m-%dT%H:%M'),
                }
            ),
            'created_to': forms.CheckboxSelectMultiple(attrs={'overflow':''})
        }
    def __init__(self, *args, **kwargs):
        board = kwargs.pop('board', None)  # Получаем доску из kwargs
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if board is not None:
            # Ограничиваем выбор пользователей — только участники доски
            self.fields['created_to'].queryset = board.members.all()
    def clean_title(self):
        """Проверка уникальности названия задачи."""
        title = self.cleaned_data.get('title')
        if self.user and Task.objects.filter(title=title, created_by=self.user).exists():
            raise forms.ValidationError("Задача с таким названием уже существует.")
        return title
    def save(self, commit=True, user=None):
        instance = super().save(commit=False)
        if user:
            instance.created_by = user  # Присваиваем текущего пользователя
        if commit:
            instance.save()
            self.save_m2m()
        return instance


class EditTaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'deadline', 'status', 'created_to']

        widgets = {
            'deadline': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control',
                }
            ),
            'created_to': forms.CheckboxSelectMultiple()
        }

    def __init__(self, *args, **kwargs):
        board = kwargs.pop('board', None)
        super().__init__(*args, **kwargs)
        if board is not None:
            self.fields['created_to'].queryset = board.members.all()
