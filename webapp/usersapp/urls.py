from django.urls import path, include
from  . import views
urlpatterns = [
    path('', views.BlankFunc),
    path('registration/', views.RegForm_Func, name='regform'),
    path('login/', views.login_view, name='login'),
    path('forgotpassword/', views.forgot_password_view, name='forgotpassword'),
    path('registration/main/', include('boardsapp.urls')),
    path('registration/login/main/', include('boardsapp.urls')),
]