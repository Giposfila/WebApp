from django.db import models
class UsersDB(models.Model):
    Email=models.EmailField('Почта', max_length=100)
    Password=models.CharField('Пароль', max_length=100)
    def __str__(self):
        return self.Email
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

