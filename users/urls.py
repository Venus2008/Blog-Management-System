from django.urls import path
# from myapp.models import Users
from .views import *

urlpatterns = [
    path('signup', RegisterView.as_view(), name='signup'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('Reset-password-request', PasswordResetRequestView.as_view(),name='password_reset_request'),
    path('Password-reset/<str:token>/', ResetPasswordView.as_view(), name='reset_password'),
]
