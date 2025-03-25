from django.urls import path, include
from  . import views
urlpatterns = [
    path('', views.MainMenu, name='main'),
    path('profile/', views.Profile_view, name='profile'),
    path('profile_edit/', views.ProfileEdit_view, name='profile_edit'),
    path('tasks/<int:pk>', views.TaskShow.as_view(), name='task-detail')
]