from django.shortcuts import render, redirect
from .forms import UsersForm
def MainMenu(request):
    return render(request,'usersapp/main.html')
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