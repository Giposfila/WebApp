from django.urls import path
from . import views

urlpatterns = [
    path('', views.BlankFunc, name='home'),
    path('register/', views.RegForm_Func, name='regform'),
    path('login/', views.login_view, name='login'),
    path('forgot-password/', views.forgot_password_view, name='forgotpassword'),
]