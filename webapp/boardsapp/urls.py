from django.urls import path, include
from  . import views
from django.contrib.auth import views as auth_views
from .views import ChangePasswordView

urlpatterns = [
    path('', views.MainMenu, name='main'),
    path('tasks/<int:pk>', views.TaskShow.as_view(), name='task-detail'),
    path('boards/<int:board_id>/', views.BoardShow.as_view(), name='board-detail'),
    path('boardcreate/', views.BoardCreate_view, name='boardcreate'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('logout/', auth_views.LogoutView.as_view(next_page='regform'), name='logout'),
    path('boards/<int:board_id>/create-task/', views.create_task, name='create-task'),
    path('tasks/<int:task_id>/add-comment/', views.add_comment, name='add-comment'),
]