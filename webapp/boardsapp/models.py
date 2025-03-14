from django.db import models

class Board(models.Model):
    title=models.CharField("Название", max_length=50)
    description=models.TextField('Описание')
    created_date=models.DateTimeField('Время создания',auto_created=True)
    def __str__(self):
        return self.title