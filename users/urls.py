from django.urls import path
from myapp.models import Users
from users import views

urlpatterns = [
    path('signup', views.register, name='signup'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('Reset-password-request', views.password_reset_request,name='password_reset_request'),
    path('Password-reset/<str:token>/', views.reset_password, name='reset_password'),
]
