from django.urls import path
from  . import views
urlpatterns = [
    path('', views.RegForm_Func),
    path('main/', views.MainMenu)
]