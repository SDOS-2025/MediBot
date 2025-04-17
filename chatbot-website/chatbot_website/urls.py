from django.contrib import admin
from django.urls import path, include
from chatbot.admin import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),  # Use our custom admin site
    path('', include('chatbot.urls')),  # Include chatbot app's URLs
]