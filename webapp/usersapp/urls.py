from django.urls import path, include
from  . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('', views.BlankFunc),
    path('admin_log/', views.Admin_button, name='admin_log'),
    path('registration/', views.RegForm_Func, name='regform'),
    path('email-confirmation/', views.email_confirmation_view, name='email_confirmation'),
    path('resend-code/', views.resend_code_view, name='resend_code'),
    path('login/', views.login_view, name='login'),
    path('forgotpassword/', views.forgot_password_view, name='forgotpassword'),
    path('main/', include('boardsapp.urls'), name='main'),
    path('profile/', views.Profile_view, name='profile'),
    path('profile_edit/', views.ProfileEdit_view, name='profile_edit'),
    path('captcha/', include('captcha.urls')),
    path('main/users/', views.users_search, name='users'),
    path('send-request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('profile/accept/<str:username>/', views.accept_friend_request, name='accept_friend_request'),
    path('profile/decline/<str:username>/', views.decline_friend_request, name='decline_friend_request'),
    path('profile/remove/<str:username>/', views.remove_friend, name='remove_friend'),
    path('friend/restore/<str:username>/', views.restore_friend_request, name='restore_friend_request')
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)