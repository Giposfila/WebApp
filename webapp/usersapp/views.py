from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.contrib.auth import login
from django.contrib.auth.models import User

from boardsapp.models import Attachment, Task, Board
from .models import EmailConfirmation, FriendRequest
import datetime
from . import models
from .forms import *
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

def BlankFunc(request):
    if request.user.is_authenticated:
        return redirect('main')
    else:
        return redirect('login')


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

def check_email(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        exists = User.objects.filter(email=email).exists()
        return JsonResponse({'exists': exists})
    return JsonResponse({'error': 'Invalid request'}, status=400)

def check_username(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        exists = User.objects.filter(username=username).exists()
        return JsonResponse({'exists': exists})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def email_confirmation_view(request):
    user_id = request.session.get('user_id_to_confirm')
    if not user_id:
        return redirect('regform')

    user = User.objects.get(id=user_id)
    last_code_sent_time = request.session.get('last_code_sent_time', None)
    if last_code_sent_time:
        # Переводим в миллисекунды для JS
        last_code_sent_time = int(last_code_sent_time * 1000)
    if request.method == 'POST':
        form = EmailConfirmationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            request.session['user_id_to_confirm'] = user.id
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

    return render(request, 'usersapp/email_confirmation.html', {'form': form, 'last_code_sent_time': last_code_sent_time})


def resend_code_view(request):
    user_id = request.session.get('user_id_to_confirm')
    if not user_id:
        return redirect('regform')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('regform')

    now = timezone.now()

    # Получаем время последней отправки как timestamp
    last_sent_time = request.session.get('last_code_sent_time', None)

    cooldown_seconds = 60
    if last_sent_time:
        time_since_last = (now - timezone.datetime.fromtimestamp(last_sent_time, tz=timezone.get_current_timezone())).total_seconds()
        if time_since_last < cooldown_seconds:
            messages.error(
                request,
                f"Повторный код можно отправить через {int(cooldown_seconds - time_since_last)} секунд."
            )
            return redirect('email_confirmation')

    # Деактивируем старые коды
    EmailConfirmation.objects.filter(user=user).update(is_used=True)

    # Генерируем новый код
    code = get_random_string(length=6, allowed_chars='0123456789')
    EmailConfirmation.objects.create(user=user, code=code)

    # Отправляем email
    send_mail(
        'Новый код подтверждения регистрации',
        f'Ваш новый код подтверждения: {code}',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

    # Сохраняем время отправки как timestamp (число)
    request.session['last_code_sent_time'] = now.timestamp()
    request.session.modified = True

    messages.success(request, "Новый код подтверждения отправлен.")
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

from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.middleware.csrf import get_token

@require_http_methods(["POST"])
def login_check_view(request):
    errors = {}
    username = request.POST.get('username')
    password = request.POST.get('password')

    if not username:
        errors['username'] = 'Введите логин или email'
    if not password:
        errors['password'] = 'Введите пароль'

    if errors:
        return JsonResponse({'success': False, 'errors': errors})

    user = authenticate(request, username=username, password=password)
    if not user:
        errors['username'] = 'Неверное имя пользователя или пароль'
        return JsonResponse({'success': False, 'errors': errors})

    return JsonResponse({
        'success': True,
        'csrf_token': get_token(request)  # Возвращаем новый CSRF токен
    })

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
@login_required
def users_search(request):
    current_user = request.user
    query = request.GET.get('q', '')
    board_id = request.GET.get('board_id')  # Получаем ID доски из параметров

    # Получаем список ID прямых друзей текущего пользователя
    direct_friends = list(
        current_user.profile.friends.values_list('user_id', flat=True)
    )

    # Получаем пользователей
    if query:
        users = User.objects.filter(username__icontains=query)
    elif board_id:
        users = User.objects.filter(profile__in=request.user.profile.friends.all()).distinct()
    else:
        # Список ID друзей друзей
        friends_of_friends_ids = set()
        for friend in current_user.profile.friends.all():
            friends = friend.friends.values_list('user_id', flat=True)
            for fid in friends:
                if fid != current_user.id and fid not in direct_friends:
                    friends_of_friends_ids.add(fid)
        users = User.objects.filter(id__in=friends_of_friends_ids)

    # Получаем все исходящие запросы
    out_requests = FriendRequest.objects.filter(
        from_user=current_user,
        visible=True
    ).values_list('to_user', flat=True)
    out_request_ids = set(out_requests)

    # Получаем все входящие запросы
    in_requests = FriendRequest.objects.filter(
        to_user=current_user,
        visible=True
    ).values_list('from_user', flat=True)
    in_request_ids = set(in_requests)

    # Получаем все отклонённые запросы
    declined_requests = FriendRequest.objects.filter(
        to_user=current_user,
        visible=False
    ).values_list('from_user', flat=True)
    declined_request_ids = set(declined_requests)

    # Получаем участников доски, если board_id указан
    board_members = []
    if board_id:
        try:
            board = Board.objects.get(id=board_id)
            board_members = board.members.all()
        except Board.DoesNotExist:
            pass

    # Добавляем статусы дружбы для каждого пользователя
    users_list = []
    for user in users:
        user.is_friend = user.id in direct_friends
        user.out_friend_request = user.id in out_request_ids
        user.in_friend_request = user.id in in_request_ids
        user.declined_request = user.id in declined_request_ids
        users_list.append(user)

    return render(request, 'boardsapp/users.html', {
        'users': users_list,
        'query': query,
        'board_id': board_id,
        'board_members': board_members
    })
from django.contrib import messages


@login_required
def add_member_to_board(request, board_id, user_id):
    board = get_object_or_404(Board, id=board_id)
    user_to_add = get_object_or_404(User, id=user_id)

    # Проверяем, что текущий пользователь - создатель доски
    if request.user != board.created_by:
        return JsonResponse({'status': 'error', 'message': 'Только создатель доски может добавлять участников'})

    # Проверяем, не является ли пользователь уже участником
    if board.members.filter(id=user_id).exists():
        return JsonResponse({'status': 'error', 'message': 'Пользователь уже является участником доски'})

    # Добавляем пользователя в доску
    board.members.add(user_to_add)

    return JsonResponse({'status': 'success', 'message': 'Пользователь успешно добавлен в доску'})

@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)

    if request.user == to_user:
        return JsonResponse({'status': 'error', 'message': 'Нельзя добавить самого себя'})

    if FriendRequest.objects.filter(from_user=request.user, to_user=to_user).exists():
        return JsonResponse({'status': 'info', 'sent_request': True})

    FriendRequest.objects.create(from_user=request.user, to_user=to_user)
    return JsonResponse({'status': 'success', 'sent_request': True})


@login_required
def accept_friend_request(request, username):
    from_user = get_object_or_404(User, username=username)

    # Находим запрос
    friend_request = FriendRequest.objects.filter(
        from_user=from_user,
        to_user=request.user
    ).first()

    if friend_request:
        # Добавляем друг друга в друзья
        request_profile, _ = Profile.objects.get_or_create(user=request.user)
        from_profile, _ = Profile.objects.get_or_create(user=from_user)

        request_profile.friends.add(from_profile)
        from_profile.friends.add(request_profile)

        # Удаляем запрос
        friend_request.delete()

    return redirect('profile-detail', username=username)

@login_required
def remove_friend(request, username):
    friend_user = get_object_or_404(User, username=username)

    try:
        current_profile = request.user.profile
        friend_profile = friend_user.profile

        # Удаляем друг друга из списков друзей
        current_profile.friends.remove(friend_profile)
        friend_profile.friends.remove(current_profile)
    except Exception as e:
        pass  # Можно добавить логику обработки ошибок

    return redirect('profile-detail', username=username)

@login_required
def decline_friend_request(request, username):
    from_user = get_object_or_404(User, username=username)

    friend_request = FriendRequest.objects.filter(
        from_user=from_user,
        to_user=request.user
    ).first()

    if friend_request:
        friend_request.visible = False  # Скрываем, но не удаляем
        friend_request.save()

    return redirect('profile-detail', username=username)

@login_required
def restore_friend_request(request, username):
    from_user = get_object_or_404(User, username=username)

    friend_request = FriendRequest.objects.filter(
        from_user=from_user,
        to_user=request.user,
        visible=False  # Только отклонённые запросы
    ).first()

    if friend_request:
        friend_request.visible = True
        friend_request.save()

    return redirect('profile-detail', username=username)


from django.contrib.auth.hashers import make_password
from django.contrib import messages


def forgot_password_view(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)

            # Генерируем код подтверждения
            code = get_random_string(length=6, allowed_chars='0123456789')
            EmailConfirmation.objects.create(user=user, code=code)

            # Отправляем email
            send_mail(
                'Восстановление пароля',
                f'Ваш код для восстановления пароля: {code}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            # Сохраняем данные в сессии
            request.session['password_reset_user_id'] = user.id
            request.session['last_code_sent_time'] = timezone.now().timestamp()

            return redirect('password_reset_confirm')
    else:
        form = ForgotPasswordForm()

    return render(request, 'usersapp/forgotpassword.html', {'form': form})


def password_reset_confirm_view(request):
    user_id = request.session.get('password_reset_user_id')
    if not user_id:
        return redirect('forgotpassword')

    user = get_object_or_404(User, id=user_id)
    last_code_sent_time = request.session.get('last_code_sent_time', None)

    if request.method == 'POST':
        form = EmailConfirmationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']

            try:
                confirmation = EmailConfirmation.objects.get(
                    user=user,
                    code=code,
                    is_used=False,
                    created_at__gte=timezone.now() - datetime.timedelta(hours=1)
                )
                confirmation.is_used = True
                confirmation.save()

                request.session['code_confirmed'] = True
                return redirect('password_reset_new')

            except EmailConfirmation.DoesNotExist:
                form.add_error('code', 'Неверный или устаревший код')
    else:
        form = EmailConfirmationForm()

    return render(request, 'usersapp/password_reset_confirm.html', {
        'form': form,
        'last_code_sent_time': last_code_sent_time
    })


def password_reset_new_view(request):
    if not request.session.get('code_confirmed'):
        return redirect('forgotpassword')

    user_id = request.session.get('password_reset_user_id')
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            # Обновляем пароль
            user.password = make_password(form.cleaned_data['new_password1'])
            user.save()

            # Очищаем сессию
            del request.session['password_reset_user_id']
            del request.session['code_confirmed']

            messages.success(request, 'Пароль успешно изменен. Теперь вы можете войти.')
            return redirect('login')
    else:
        form = ResetPasswordForm()

    return render(request, 'usersapp/password_reset_new.html', {'form': form})

def resend_password_code_view(request):
    user_id = request.session.get('password_reset_user_id')
    if not user_id:
        return redirect('forgotpassword')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('forgotpassword')

    now = timezone.now()
    last_sent_time = request.session.get('last_code_sent_time', None)

    cooldown_seconds = 60
    if last_sent_time:
        time_since_last = (now - timezone.datetime.fromtimestamp(last_sent_time, tz=timezone.get_current_timezone())).total_seconds()
        if time_since_last < cooldown_seconds:
            messages.error(
                request,
                f"Повторный код можно отправить через {int(cooldown_seconds - time_since_last)} секунд."
            )
            return redirect('password_reset_confirm')

    # Деактивируем старые коды
    EmailConfirmation.objects.filter(user=user).update(is_used=True)

    # Генерируем новый код
    code = get_random_string(length=6, allowed_chars='0123456789')
    EmailConfirmation.objects.create(user=user, code=code)

    # Отправляем email
    send_mail(
        'Новый код для сброса пароля',
        f'Ваш новый код: {code}',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

    # Сохраняем время отправки
    request.session['last_code_sent_time'] = now.timestamp()
    request.session.modified = True

    messages.success(request, "Новый код подтверждения отправлен.")
    return redirect('password_reset_confirm')
