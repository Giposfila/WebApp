from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib.auth import login
from django.contrib.auth.models import User
from .models import EmailConfirmation, FriendRequest
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
        'etasks12@mail.ru',
        [user.email],
        fail_silently=False,
    )

    return redirect('email_confirmation')

def Admin_button(request):
    user=User.objects.get(username='Admin')
    login(request, user)  # Создаем сессию для пользователя
    return redirect('main')  # Перенаправляем на главную страницу

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
    email_confirmation_view(request)
    form = EmailConfirmationForm(request.POST)
    return render(request, 'usersapp/forgotpassword.html')
@login_required
def Profile_view(request):
    data={
        'username':request.user.username,
        "email":request.user.email,
        "profile": request.user.profile
          }
    return render(request, 'boardsapp/AnotherProfile.html',data)
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
    current_user = request.user
    # Все прямые друзья текущего пользователя
    direct_friends = current_user.profile.friends.all().values_list('user', flat=True)

    # Список ID'ов друзей друзей
    friends_of_friends_ids = set()

    for friend in current_user.profile.friends.all():
        # Друзья этого друга
        friends = friend.user.profile.friends.all().values_list('user_id', flat=True)
        for user_id in friends:
            if user_id != current_user.id and user_id not in direct_friends:
                friends_of_friends_ids.add(user_id)

    # Получаем сами объекты User
    users = User.objects.filter(id__in=friends_of_friends_ids)
    all_users=User.objects.all()
    query = request.GET.get('q', '')  # Получаем строку поиска
    if query:
        users = all_users.filter(Q(username__icontains=query))  # Поиск по username
    data = {
        'users':users,
    }
    return render(request, 'boardsapp/users.html', data)

from django.contrib import messages
@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)

    if request.user == to_user:
        return JsonResponse({'status': 'error', 'message': 'Нельзя добавить самого себя'})

    if FriendRequest.objects.filter(from_user=request.user, to_user=to_user).exists():
        return JsonResponse({'status': 'info', 'sent_request': True})

    FriendRequest.objects.create(from_user=request.user, to_user=to_user)
    return JsonResponse({'status': 'success', 'sent_request': True})