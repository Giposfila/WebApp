from django.db import models
from django.contrib.auth.models import User

class Board(models.Model):
    title=models.CharField("Название", max_length=50)
    description=models.TextField('Описание')
    created_date=models.DateTimeField('Время создания',auto_created=True, auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_boards')
    members=models.ManyToManyField(User, related_name='boards', blank=True)

    def __str__(self):
        return self.title
class Task(models.Model):
    title = models.CharField("Название", max_length=50)
    description = models.TextField('Описание')
    board=models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tasks')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='tasks', null=True, blank=True)
    created_to = models.ManyToManyField(User, related_name='tasks_to_do', blank=True)
    created_date = models.DateTimeField('Время создания', auto_created=True)
    deadline=models.DateTimeField('Дедлайн', auto_created=True, blank=True, )
    def __str__(self):
        return self.title