from django.urls import path
from  . import views
urlpatterns = [
    path('', views.BlankFunc),
    path('registration/', views.RegForm_Func, name='regform'),
    path('registration/login/', views.login_view, name='login'),
    path('registration/login/forgotpassword/', views.forgot_password_view, name='forgotpassword'),
    path('registration/main/', views.MainMenu, name='main'),
    path('registration/login/main/', views.MainMenu, name='main'),
    path('registration/main/profile/', views.Profile_view, name='profile'),
    path('registration/login/main/profile/', views.Profile_view, name='profile')
]