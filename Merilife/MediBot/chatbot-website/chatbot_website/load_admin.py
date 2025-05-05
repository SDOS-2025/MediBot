from django.contrib import admin
from django.urls import path
from .load_views import load_dashboard
from chatbot.admin import admin_site  # Import the custom admin site

# Create a simple model to attach our admin to
class LoadManagerAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        load_manager_urls = [
            path('', load_dashboard, name='load_dashboard_admin'),
        ]
        return load_manager_urls + urls

# This is a placeholder model - it doesn't actually exist in the database
# but allows us to add a custom admin interface
class LoadManagerModel:
    class Meta:
        app_label = 'chatbot_website'
        verbose_name = 'Load Manager'
        verbose_name_plural = 'Load Manager'
        
    def __str__(self):
        return 'Load Manager'

# Register with custom admin site
admin_site.register([LoadManagerModel], LoadManagerAdmin)

# Also register with default admin site for compatibility
admin.site.register([LoadManagerModel], LoadManagerAdmin) 