from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import LoginForm
from .forms import UsersForm
from django.contrib.auth.models import User
def MainMenu(request):
    users=User.objects.all()
    data={'users':users}
    return render(request,'usersapp/main.html',data)
def RegForm_Func(request):
    error=''
    if request.method=='POST':
        form=UsersForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('main/')
        else:
            error='Форма была неверной'
    form=UsersForm()
    data={'form':form, 'error': error}
    return render(request, 'usersapp/regform.html', data)

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)  # Создаем сессию для пользователя
            return redirect('main/')  # Перенаправляем на главную страницу
    else:
        form = LoginForm()
    return render(request, 'usersapp/login.html', {'form': form})