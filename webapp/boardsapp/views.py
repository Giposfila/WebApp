from django.shortcuts import render, redirect
from django.views.generic import DetailView
from .forms import *

from .models import Board, Task
def MainMenu(request):
    boards=request.user.boards.all()
    tasks = Task.objects.all()
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



def BoardCreate_view(request):
    if request.method == 'POST':
        form = CreateBoardForm(request.POST)
        if form.is_valid():
            form.save(user=request.user)  # Передаем текущего пользователя
            return redirect('main')  # Перенаправляем на список задач
    else:
        form = CreateBoardForm()
    return render(request, 'boardsapp/boardcreate.html', {'form': form, "profile": request.user.profile})