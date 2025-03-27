from django.db import models
from django.contrib.auth.models import User

class Board(models.Model):
    title=models.CharField("Название", max_length=50)
    description=models.TextField('Описание')
    created_date=models.DateTimeField('Время создания',auto_created=True, auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='boards')
    def __str__(self):
        return self.title
class Task(models.Model):
    title = models.CharField("Название", max_length=50)
    description = models.TextField('Описание')
    # Column
    # createdby
    created_date = models.DateTimeField('Время создания', auto_created=True)
    deadline=models.DateTimeField('Дедлайн', auto_created=True, blank=True, )
    def __str__(self):
        return self.title