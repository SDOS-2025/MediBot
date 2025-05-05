from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve  # Add this import
from chatbot.admin import admin_site
from chatbot.views.views import register_doctor
from .load_views import load_dashboard, load_status_api

urlpatterns = [
    path('admin/register_doctor/', register_doctor, name='register_doctor'),
    # Load manager URLs - moved before the admin url pattern
    path('admin/load/', load_dashboard, name='load_dashboard'),
    path('admin/', admin_site.urls),  # Use our custom admin site
    path('', include('chatbot.urls')),
    path('reports/', include('reports.urls')),  # Add reports URL patterns
    path('api/load-status/', load_status_api, name='load_status_api'),
]

if settings.DEBUG:
    urlpatterns += [
        path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
    ]