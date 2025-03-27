from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .forms import LoginForm, UsersForm

def BlankFunc(request):
    return redirect('regform')

def RegForm_Func(request):
    if request.method == 'POST':
        form = UsersForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('main')
    else:
        form = UsersForm()
    return render(request, 'usersapp/regform.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('main')
    else:
        form = LoginForm(request)
    return render(request, 'usersapp/login.html', {'form': form})

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        messages.success(request, 'Инструкции отправлены на ваш email')
        return redirect('login')
    return render(request, 'usersapp/forgotpassword.html')