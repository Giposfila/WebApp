from datetime import timezone
from django.views.generic import UpdateView, DeleteView
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import DetailView
from .forms import *
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import  *
def MainMenu(request):
    boards=request.user.boards.all()
    tasks = request.user.tasks_to_do.all()
    data={'boards':boards,
          'tasks':tasks,
          "profile": request.user.profile,
          'user':request.user,
          'now':timezone.now()
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

class BoardShow(DetailView):
    model = Board
    template_name = 'boardsapp/board.html'
    context_object_name = 'board'
    pk_url_kwarg = 'board_id'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = self.object.tasks.all()
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