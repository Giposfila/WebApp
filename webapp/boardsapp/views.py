from django.shortcuts import render
from .models import Board
def MainMenu(request):
    boards=Board.objects.all()
    data={'boards':boards}
    return render(request,'boardsapp/main.html',data)
def Profile_view(request):
    data={
        'username':request.user.username,
        "email":request.user.email
          }
    return render(request, 'boardsapp/profile.html',data)