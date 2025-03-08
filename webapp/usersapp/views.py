from django.shortcuts import render, redirect
from .forms import UsersForm
from django.contrib.auth.models import User
def MainMenu(request):
    users=User.objects.all()
    data={'users':users}
    return render(request,'usersapp/main.html',data)
def RegForm_Func(request):
    error=''
    if request.method=='POST':
        form=UsersForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('main/')
        else:
            error='Форма была неверной'
    form=UsersForm()
    data={'form':form, 'error': error}
    return render(request, 'usersapp/regform.html', data)