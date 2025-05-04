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
    path('tasks/<int:task_id>/add-comment/', views.add_comment, name='add-comment'),
    path('tasks/<int:pk>/edit/', views.TaskEdit.as_view(), name='task-edit'),
    path('tasks/<int:pk>/delete/', views.TaskDelete.as_view(), name='task-delete'),
    path('tasks/<int:pk>/complete/', views.complete_task, name='complete-task'),
    path('tasks/<int:pk>/confirm/', views.confirm_completion, name='confirm-completion'),
]