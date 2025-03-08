from django.urls import path
from  . import views
urlpatterns = [
    path('', views.RegForm_Func, name='regform'),
    path('login/', views.login_view, name='login'),
    path('main/', views.MainMenu, name='main'),
    path('login/main/', views.MainMenu, name='main')
]