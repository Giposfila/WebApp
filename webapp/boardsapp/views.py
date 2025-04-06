from django.shortcuts import render, redirect
from django.views.generic import DetailView
from .forms import *
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy

from .models import Board, Task
def MainMenu(request):
    boards=request.user.boards.all()
    tasks = request.user.tasks_to_do.all()
    data={'boards':boards,
          'tasks':tasks,
          "profile": request.user.profile
          }
    return render(request,'boardsapp/main.html',data)

class TaskShow(DetailView):
    model = Task
    boards=Board.objects.all()
    template_name = 'boardsapp/task.html'
    context_object_name = 'task'

class BoardShow(DetailView):
    model = Board
    boards=Board.objects.all()
    template_name = 'boardsapp/board.html'
    context_object_name = 'board'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = self.object.tasks.all()
        return context


def BoardCreate_view(request):
    if request.method == 'POST':
        form = CreateBoardForm(request.POST)
        if form.is_valid():
            form.save(user=request.user)  # Передаем текущего пользователя
            return redirect('main')  # Перенаправляем на список задач
    else:
        form = CreateBoardForm()
    return render(request, 'boardsapp/boardcreate.html', {'form': form, "profile": request.user.profile})

class ChangePasswordView(PasswordChangeView):
    template_name = 'boardsapp/change_password.html'
    success_url = reverse_lazy('profile')