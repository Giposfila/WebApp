from django.urls import path, include
from  . import views
urlpatterns = [
    path('', views.MainMenu),
    path('profile/', views.Profile_view)
]