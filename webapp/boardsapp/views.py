from django.shortcuts import render
from django.views.generic import DetailView


from .models import Board, Task
def MainMenu(request):
    boards=Board.objects.all()
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