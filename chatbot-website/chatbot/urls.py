from django.urls import path
from .views.views import index, user_login, register_user, chat, generate_pdf, pdf_preview
from django.conf.urls.static import static
from django.conf import settings  # Add this

urlpatterns = [
    path('', index, name='index'),
    path('login/', user_login, name='login'),
    path('register/', register_user, name='register'),
    path('chat/', chat, name='chat'),
    path('generate-pdf/', generate_pdf, name='generate_pdf'),
    path('pdf-preview/', pdf_preview, name='pdf_preview'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)