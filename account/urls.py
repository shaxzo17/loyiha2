from django.urls import path
from .views import (signup_view, login_view, logout_view, profile_update_view, change_password_view, reset_pass, reset2, send_code_view,verify_code_view)

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/update/', profile_update_view, name='profile-update'),
    path('profile/change-password/', change_password_view, name='change-pass'),
    path('reset1/', reset_pass, name='reset1'),
    path('reset2/', reset2, name='reset2'),
    path('send-code/', send_code_view, name='send-code'),
    path('verify-code/', verify_code_view, name='verify-code'),
]