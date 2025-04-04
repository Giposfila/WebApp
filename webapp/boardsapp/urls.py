from django.urls import path, include
from  . import views
from django.contrib.auth import views as auth_views
from .views import ChangePasswordView

urlpatterns = [
    path('', views.MainMenu, name='main'),
    path('tasks/<int:pk>', views.TaskShow.as_view(), name='task-detail'),
    path('boards/<int:pk>', views.BoardShow.as_view(), name='board-detail'),
    path('boardcreate/', views.BoardCreate_view, name='boardcreate'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
]