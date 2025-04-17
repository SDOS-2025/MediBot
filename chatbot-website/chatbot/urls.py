from django.urls import path
from .views.views import index, user_login, register_user, chat, doctor_dashboard, register_doctor, user_logout, generate_pdf, pdf_preview, close_treatment
from django.conf.urls.static import static
from django.conf import settings
from .views.views import report_gen

urlpatterns = [
    path('', index, name='index'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('register/', register_user, name='register'),
    path('register_doctor/', register_doctor, name='register_doctor'),  # Admin-only doctor registration
    path('chat/', chat, name='chat'),
    path('doctor_dashboard/', doctor_dashboard, name='doctor_dashboard'),
    path('treatment/close/<int:treatment_id>/', close_treatment, name='close_treatment'),  # Close treatment
    path('generate-pdf/', generate_pdf, name='generate_pdf'),
    path('pdf-preview/', pdf_preview, name='pdf_preview'),
    path('reportgen/', report_gen, name='reportgen'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)