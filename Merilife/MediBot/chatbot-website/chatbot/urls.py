from django.urls import path
from .views.views import index, user_login, register_user, chat, doctor_dashboard, register_doctor, user_logout, generate_pdf, pdf_preview, close_treatment, view_treatment_history
from django.conf.urls.static import static
from django.conf import settings
from .views.views import reportgen, medical_chat
from . import views
from .views import views as chatbot_views

urlpatterns = [
    # path('admin/register_doctor/', register_doctor, name='register_doctor'),  # Admin-only doctor registration
    path('', index, name='index'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('register/', register_user, name='register'),
    path('chat/', chat, name='chat'),
    path('doctor_dashboard/', doctor_dashboard, name='doctor_dashboard'),
    path('treatment/close/<int:treatment_id>/', close_treatment, name='close_treatment'),  # Close treatment
    path('treatment/history/<int:treatment_id>/', view_treatment_history, name='view_treatment_history'),
    path('generate-pdf/', generate_pdf, name='report_gen'),
    path('pdf-preview/', pdf_preview, name='pdf_preview'),
    path('reportgen/', reportgen, name='reportgen'),
    path('medical-chat/', medical_chat, name='medical_chat'),
    path('api/speech-to-text/', chatbot_views.speech_to_text, name='speech_to_text'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)