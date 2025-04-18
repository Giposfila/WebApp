from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import *
from django.contrib.auth.models import User
from django.http import JsonResponse

def BlankFunc(request):
    return redirect('/registration/')
def RegForm_Func(request):
    if request.method == 'POST':
        form = UsersForm(request.POST)
        if form.is_valid():
            # Сохраняем пользователя и получаем объект
            user = form.save()
            # Авторизуем пользователя
            login(request, user)
            return redirect('main')  # Перенаправляем на главную страницу
    else:
        form = UsersForm()

    return render(request, 'usersapp/regform.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            return redirect('main')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'Неверное имя пользователя или пароль'
            }, status=400)
    else:
        form = LoginForm()

    return render(request, 'usersapp/login.html', {'form': form})

def forgot_password_view(request):
    return render(request, 'usersapp/forgotpassword.html')
def Profile_view(request):
    data={
        'username':request.user.username,
        "email":request.user.email,
        "profile": request.user.profile
          }
    return render(request, 'boardsapp/profile.html',data)


@login_required
def ProfileEdit_view(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        user_form = ChangeUserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile = profile_form.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'avatar_url': profile.avatar.url if profile.avatar else ''
                })
            return redirect('profile')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': 'Ошибка при сохранении'
            }, status=400)
    else:
        user_form = ChangeUserForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': user.profile
    }
    return render(request, 'boardsapp/profile_edit.html', context)