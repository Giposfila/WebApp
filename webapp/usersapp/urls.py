from django.urls import path, include
from  . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.BlankFunc),
    path('registration/', views.RegForm_Func, name='regform'),
    path('login/', views.login_view, name='login'),
    path('forgotpassword/', views.forgot_password_view, name='forgotpassword'),
    path('main/', include('boardsapp.urls'), name='main'),
    path('profile/', views.Profile_view, name='profile'),
    path('profile_edit/', views.ProfileEdit_view, name='profile_edit'),
    path('captcha/', include('captcha.urls')),
    path('main/users/', views.users_search, name='users'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)