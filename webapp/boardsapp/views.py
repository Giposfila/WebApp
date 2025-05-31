from datetime import timezone

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import UpdateView, DeleteView
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import DetailView

from usersapp.models import FriendRequest, Profile
from .forms import *
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from .models import  *
def MainMenu(request):
    boards=request.user.boards.all()
    tasks = request.user.tasks_to_do.all()
    status = request.GET.get('status')
    if status and status!='all':
        tasks = tasks.filter(status=status)
    data={'boards':boards,
          'tasks':tasks,
          "profile": request.user.profile,
          'user':request.user,
          'now':timezone.now(),
          'status':status
          }
    return render(request,'boardsapp/main.html',data)

class TaskShow(DetailView):
    model = Task
    template_name = 'boardsapp/task.html'
    context_object_name = 'task'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task = self.object

        # Проверяем, не просрочена ли задача
        if task.deadline and task.deadline < timezone.now() and task.status == 'В процессе':
            task.status = 'Просрочено'
            task.save()

        context['executors'] = task.created_to.all()
        return context


@login_required
def create_task(request, board_id):
    board = get_object_or_404(Board, id=board_id)

    if request.method == 'POST':
        form = CreateTaskForm(request.POST, board=board, user=request.user)
        if form.is_valid():
            task = form.save(user=request.user,commit=False)
            task.board = board
            task.save()
            form.save_m2m()  # Сохраняем ManyToMany поля (executors)
            return redirect(reverse('board-detail', kwargs={'board_id': board.id}))
    else:
        form = CreateTaskForm(board=board, user=request.user)

    return render(request, 'boardsapp/board.html', {
        'form': form,
        'board': board,
        'user':request.user
    })

@login_required
def delete_board(request, board_id):
    board = get_object_or_404(Board, id=board_id)

    # Проверяем, является ли пользователь создателем доски
    if request.user != board.created_by:
        messages.error(request, "Только создатель доски может удалить её.")
        return redirect('board-detail', board_id=board_id)

    # Удаляем доску (все задачи и связи будут удалены каскадно)
    board.delete()
    messages.success(request, "Доска успешно удалена.")
    return redirect('main')  # Перенаправление на главную страницу

@login_required
def remove_member(request, board_id, user_id):
    board = get_object_or_404(Board, id=board_id)

    # Проверяем, является ли пользователь создателем доски
    if request.user != board.created_by:
        messages.error(request, "Только создатель доски может удалять участников.")
        return redirect('board-detail', board_id=board_id)

    # Находим пользователя, которого нужно удалить
    user_to_remove = get_object_or_404(board.members, id=user_id)

    # Убедимся, что нельзя удалить самого себя
    if user_to_remove == request.user:
        messages.error(request, "Нельзя удалить самого себя из доски.")
        return redirect('board-detail', board_id=board_id)

    # Удаляем пользователя из доски
    board.members.remove(user_to_remove)
    messages.success(request, f"Пользователь {user_to_remove.username} удален из доски.")
    return redirect('board-detail', board_id=board_id)

class BoardShow(DetailView):
    model = Board
    template_name = 'boardsapp/board.html'
    context_object_name = 'board'
    pk_url_kwarg = 'board_id'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        board = self.get_object()
        status = self.request.GET.get('filter')
        tasks = Task.objects.filter(board=board)
        if status and status!='all':
            tasks = tasks.filter(status=status)
        context['tasks'] = tasks
        context['status'] = status
        context['members'] = self.object.members.all()
        context['form'] = CreateTaskForm(board=self.object)
        return context
    def post(self, request, *args, **kwargs):
        # Получаем объект доски
        self.object = self.get_object()
        # Инициализируем форму данными из запроса
        form = CreateTaskForm(request.POST)

        # Проверяем валидность формы
        if form.is_valid():
            task = form.save(commit=False)
            task.board = self.object  # Привязываем задачу к текущей доске
            task.save()
            form.save_m2m()
            return redirect('board-detail', board_id=self.object.id)  # Перезагружаем страницу

        # 1Если форма невалидна — возвращаем ту же страницу с формой и ошибками
        context = self.get_context_data(object=self.object)
        context['form'] = form
        return self.render_to_response(context)



def BoardCreate_view(request):
    if request.method == 'POST':
        form = CreateBoardForm(request.POST, user=request.user)
        if form.is_valid():
            form.save(user=request.user)  # Передаем текущего пользователя
            return redirect('main')  # Перенаправляем на список задач
    else:
        form = CreateBoardForm()
    return render(request, 'boardsapp/boardcreate.html', {'form': form, "profile": request.user.profile})

from django.shortcuts import get_object_or_404, redirect
from .models import Task, Board
from django.contrib.auth.decorators import login_required



class ChangePasswordView(PasswordChangeView):
    template_name = 'boardsapp/change_password.html'
    success_url = reverse_lazy('profile')


@login_required
def add_comment(request, task_id):
     task = get_object_or_404(Task, id=task_id)
     if request.method == 'POST':
         content = request.POST.get('content')
         if content:
             Comment.objects.create(
                 content=content,
                 task=task,
                 user=request.user
             )
             messages.success(request, 'Комментарий добавлен')
         else:
             messages.error(request, 'Комментарий не может быть пустым')
     return redirect('task-detail', pk=task_id)


class TaskEdit(UpdateView):
    model = Task
    form_class = EditTaskForm
    template_name = 'boardsapp/task_edit.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['board'] = self.get_object().board
        return kwargs

    def get_success_url(self):
        return reverse('task-detail', kwargs={'pk': self.object.pk})


class TaskDelete(DeleteView):
    model = Task
    template_name = 'boardsapp/task_confirm_delete.html'

    def get_success_url(self):
        return reverse('board-detail', kwargs={'board_id': self.object.board.id})


@login_required
def complete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)

    # Проверяем, что пользователь является исполнителем задачи
    if request.user in task.created_to.all():
        # Меняем статус на "В ожидании проверки"
        task.status = 'В Ожидании проверки'
        task.save()
        messages.success(request, 'Задача отправлена на проверку!')
    else:
        messages.error(request, 'Вы не можете отчитаться по этой задаче')

    return redirect('task-detail', pk=task.pk)


@login_required
def confirm_completion(request, pk):
    task = get_object_or_404(Task, pk=pk)

    # Проверяем, что пользователь является создателем задачи
    if request.user == task.created_by and task.status == 'В Ожидании проверки':
        task.status = 'Выполнено'
        task.save()
        messages.success(request, 'Выполнение задачи подтверждено!')
    else:
        messages.error(request, 'Вы не можете подтвердить выполнение этой задачи')

    return redirect('task-detail', pk=task.pk)

class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'boardsapp/AnotherProfile.html'
    context_object_name = 'user'  # Чтобы в шаблоне был доступен как {{ user }}
    slug_field = 'username'       # Используем username в URL
    slug_url_kwarg = 'username'   # Имя параметра в URL
    def get_object(self, queryset=None):
        # Получаем пользователя по username или 404
        return get_object_or_404(User, username=self.kwargs.get('username'))

    # views.py

    # views.py

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile_user = self.object
        current_user = self.request.user

        # Проверяем исходящий запрос (visible=True)
        out_friend_request = FriendRequest.objects.filter(
            from_user=current_user,
            to_user=profile_user,
            visible=True
        ).exists()

        # Проверяем входящий запрос (visible=True)
        in_friend_request = FriendRequest.objects.filter(
            from_user=profile_user,
            to_user=current_user,
            visible=True
        ).exists()

        # Проверяем, был ли запрос отклонён (visible=False)
        declined_request = FriendRequest.objects.filter(
            from_user=current_user,
            to_user=profile_user,
            visible=False
        ).exists()

        # Проверяем, есть ли отклонённый входящий запрос, который можно восстановить
        can_restore_request = FriendRequest.objects.filter(
            from_user=profile_user,
            to_user=current_user,
            visible=False
        ).exists()

        # Проверяем, являются ли друзьями
        is_friend = False
        try:
            is_friend = current_user.profile.friends.filter(user=profile_user).exists()
        except:
            pass

        context.update({
            'out_friend_request': out_friend_request,
            'in_friend_request': in_friend_request,
            'is_friend': is_friend,
            'declined_request': declined_request,
            'can_restore_request': can_restore_request,  # Новое поле
        })

        return context

def upload_attachment(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    # Проверка прав
    if request.user != task.created_by and request.user != task.board.created_by:
        messages.error(request, 'У вас нет прав прикреплять файлы к этой задаче.')
        return redirect('task-detail', task_id=task.id)

    if request.method == 'POST':
        form = AttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            # Указываем пользователя, который загрузил файл
            Attachment.objects.create(task=task, file=uploaded_file, uploaded_by=request.user)
            messages.success(request, 'Файл успешно загружен.')
            return redirect('task-detail', pk=task.id)
    else:
        form = AttachmentForm()

    return redirect('task-detail', pk=task.id)
def delete_attachment(request, file_id):
    file = get_object_or_404(Attachment, id=file_id)

    # Проверка: только автор файла или создатель задачи может удалить
    if request.user != file.uploaded_by and request.user != file.task.created_by:
        messages.error(request, 'У вас нет прав удалить этот файл.')
        return redirect('task-detail', pk=file.task.id)

    task_id = file.task.id
    file.delete()
    messages.success(request, 'Файл успешно удален.')
    return redirect('task-detail', pk=task_id)

