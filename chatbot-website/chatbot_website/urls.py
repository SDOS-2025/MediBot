from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve  # Add this import
from chatbot.admin import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),  # Use our custom admin site
    path('', include('chatbot.urls')),
    path('reports/', include('reports.urls')),  # Add reports URL patterns
]

if settings.DEBUG:
    urlpatterns += [
        path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
    ]