from django.urls import path, include
from  . import views
urlpatterns = [
    path('', views.MainMenu, name='main'),
    path('tasks/<int:pk>', views.TaskShow.as_view(), name='task-detail')
]