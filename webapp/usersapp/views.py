from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib.auth import login
from django.contrib.auth.models import User
from .models import EmailConfirmation
import datetime
from . import models
from .forms import *
from django.contrib.auth.models import User

def BlankFunc(request):
    return redirect('/registration/')


def RegForm_Func(request):
    if request.method == 'POST':
        form = UsersForm(request.POST)
        if form.is_valid():
            # Сохраняем пользователя, но не активируем сразу
            user = form.save(commit=False)
            user.is_active = False  # Пользователь не активен до подтверждения email
            user.save()

            # Создаем код подтверждения
            code = get_random_string(length=6, allowed_chars='0123456789')
            EmailConfirmation.objects.create(user=user, code=code)

            # Отправляем email с кодом
            send_mail(
                'Код подтверждения регистрации',
                f'Ваш код подтверждения: {code}',
                'etasks12@mail.ru',
                [user.email],
                fail_silently=False,
            )

            # Сохраняем u2ser_id в сессии для подтверждения
            request.session['user_id_to_confirm'] = user.id
            return redirect('email_confirmation')
    else:
        form = UsersForm()

    return render(request, 'usersapp/regform.html', {'form': form})


def email_confirmation_view(request):
    user_id = request.session.get('user_id_to_confirm')
    if not user_id:
        return redirect('regform')

    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        form = EmailConfirmationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                confirmation = EmailConfirmation.objects.get(
                    user=user,
                    code=code,
                    is_used=False,
                    created_at__gte=datetime.datetime.now() - datetime.timedelta(hours=24)
                )
                confirmation.is_used = True
                confirmation.save()

                # Активируем пользователя
                user.is_active = True
                user.save()

                # Авторизуем пользователя
                login(request, user)
                del request.session['user_id_to_confirm']
                return redirect('main')
            except EmailConfirmation.DoesNotExist:
                form.add_error('code', 'Неверный код подтверждения')
    else:
        form = EmailConfirmationForm()

    return render(request, 'usersapp/email_confirmation.html', {'form': form})


def resend_code_view(request):
    user_id = request.session.get('user_id_to_confirm')
    if not user_id:
        return redirect('regform')

    user = User.objects.get(id=user_id)

    # Деактивируем старые коды
    EmailConfirmation.objects.filter(user=user).update(is_used=True)

    # Создаем новый код
    code = get_random_string(length=6, allowed_chars='0123456789')
    EmailConfirmation.objects.create(user=user, code=code)

    # Отправляем email с новым кодом
    send_mail(
        'Новый код подтверждения регистрации',
        f'Ваш новый код подтверждения: {code}',
        'from@example.com',
        [user.email],
        fail_silently=False,
    )

    return redirect('email_confirmation')


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)  # Создаем сессию для пользователя
            return redirect('main')  # Перенаправляем на главную страницу
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
    profile = user.profile  # Получаем связанный профиль

    if request.method == 'POST':
        user_form = ChangeUserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')  # Перенаправляем на страницу профиля после сохранения
    else:
        user_form = ChangeUserForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile':user.profile
    }
    return render(request, 'boardsapp/profile_edit.html', context)
def users_search(request):
    data = {
        'users': User.objects.all()
    }

    return render(request, 'boardsapp/users.html', data)