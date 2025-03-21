from django.shortcuts import render
from django.views.generic import DetailView

from .models import Board, Task
def MainMenu(request):
    boards=Board.objects.all()
    tasks = Task.objects.all()
    data={'boards':boards,
          'tasks':tasks
          }
    return render(request,'boardsapp/main.html',data)

class TaskShow(DetailView):
    model = Task
    boards=Board.objects.all()
    template_name = 'boardsapp/task.html'
    context_object_name = 'task'

def Profile_view(request):
    data={
        'username':request.user.username,
        "email":request.user.email
          }
    return render(request, 'boardsapp/profile.html',data)
def ProfileEdit_view(request):
    data = {
        'username': request.user.username,
        "email": request.user.email
    }
    return render(request, 'boardsapp/profile_edit.html', data)