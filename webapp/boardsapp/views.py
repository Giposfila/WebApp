from django.shortcuts import render, redirect
from django.views.generic import DetailView
from .forms import *
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import  *
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
def MainMenu(request):
    boards=request.user.boards.all()
    tasks = request.user.tasks_to_do.all()
    data={'boards':boards,
          'tasks':tasks,
          "profile": request.user.profile,
          'user':request.user
          }
    return render(request,'boardsapp/main.html',data)

#a
class TaskShow(DetailView):
    model = Task
    template_name = 'boardsapp/task.html'
    context_object_name = 'task'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['executors'] = self.object.created_to.all()
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
        return context


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


@login_required
def create_task(request, board_id):
    board = get_object_or_404(Board, id=board_id)
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        deadline = request.POST.get('deadline')
        created_to = request.POST.getlist('created_to')  # Список ID пользователей

        # Создаем задачу
        task = Task.objects.create(
            title=title,
            description=description,
            board=board,
            created_by=request.user,
            deadline=deadline if deadline else None
        )

        # Назначаем исполнителей
        task.created_to.add(*created_to)

        return redirect('board-detail', board_id=board.id)

    return redirect('board-detail', board_id=board.id)

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