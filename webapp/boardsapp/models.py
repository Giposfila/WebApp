from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os



class Board(models.Model):
    title=models.CharField("Название", max_length=100)
    description=models.TextField('Описание')
    created_date=models.DateTimeField('Время создания',auto_created=True, auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_boards')
    members=models.ManyToManyField(User, related_name='boards', blank=True)

    def __str__(self):
        return self.title
class Task(models.Model):
    STATUS_CHOICES = [
        ('В процессе', 'В процессе'),
        ('Выполнено', 'Выполнено'),
        ('В Ожидании проверки', 'В Ожидании проверки'),
        ('Просрочено', 'Просрочено'),
    ]
    title = models.CharField("Название", max_length=50)
    description = models.TextField('Описание')
    board=models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tasks')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='tasks', null=True, blank=True)
    created_to = models.ManyToManyField(User,verbose_name='Ответственные за задачу', related_name='tasks_to_do', blank=True)
    created_date = models.DateTimeField('Время создания', auto_now_add=True)
    deadline=models.DateTimeField('Дедлайн', blank=True, null=True)
    status=models.CharField("Статус",max_length=20, choices=STATUS_CHOICES, default='В процессе')
    def __str__(self):
        return self.title
class Attachment(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название файла', blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='uploads/%Y/%m/%d/', verbose_name='Файл', null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attachments')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        # Получаем имя файла без пути и расширения
        if not self.name:
            filename = os.path.splitext(os.path.basename(self.file.name))[0]
            self.name = filename
        super().save(*args, **kwargs)
    def get_filename(self):
        return os.path.basename(self.file.name)
    def __str__(self):
        return self.name

class Comment(models.Model):
    content = models.TextField("Содержание", null=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField("Дата создания",auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'Комментарий от {self.user.username} к задаче {self.task.title}'