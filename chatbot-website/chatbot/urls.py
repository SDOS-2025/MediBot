from django.urls import path
from .views.views import index, user_login, register_user, chat, doctor_dashboard, register_doctor, user_logout

urlpatterns = [
    path('', index, name='index'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('register/', register_user, name='register'),
    path('register_doctor/', register_doctor, name='register_doctor'),  # Admin-only doctor registration
    path('chat/', chat, name='chat'),
    path('doctor_dashboard/', doctor_dashboard, name='doctor_dashboard'),
]