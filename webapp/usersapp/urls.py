from django.urls import path, include
from  . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import login_check_view
urlpatterns = [
    path('', views.BlankFunc),
    path('admin_log/', views.Admin_button, name='admin_log'),
    path('registration/', views.RegForm_Func, name='regform'),
    path('email-confirmation/', views.email_confirmation_view, name='email_confirmation'),
    path('resend-code/', views.resend_code_view, name='resend_code'),
    path('login/', views.login_view, name='login'),
    path('check-login/', login_check_view, name='check_login'),
    path('forgotpassword/', views.forgot_password_view, name='forgotpassword'),
    path('check-email/', views.check_email, name='check_email'),
    path('check-username/', views.check_username, name='check_username'),
    path('main/', include('boardsapp.urls'), name='main'),
    path('profile/', views.Profile_view, name='profile'),
    path('profile_edit/', views.ProfileEdit_view, name='profile_edit'),
    path('captcha/', include('captcha.urls')),
    path('main/users/', views.users_search, name='users'),
    path('send-request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('profile/accept/<str:username>/', views.accept_friend_request, name='accept_friend_request'),
    path('profile/decline/<str:username>/', views.decline_friend_request, name='decline_friend_request'),
    path('profile/remove/<str:username>/', views.remove_friend, name='remove_friend'),
    path('friend/restore/<str:username>/', views.restore_friend_request, name='restore_friend_request'),
    path('boards/<int:board_id>/add-member/<int:user_id>/', views.add_member_to_board, name='add-member-to-board'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)