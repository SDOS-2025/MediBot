from django.urls import path
from .views.views import index, user_login, register_user, chat

urlpatterns = [
    path('', index, name='index'),
    path('login/', user_login, name='login'),
    path('register/', register_user, name='register'),
    path('chat/', chat, name='chat'),
]