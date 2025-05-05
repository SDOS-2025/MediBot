from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from .models import LoadManager

class LoadManagerAdminSite(admin.AdminSite):
    """Admin site with load manager integration"""
    site_header = "Medico Administration"
    site_title = "Medico Admin Portal"
    index_title = "Medico Admin"

    def each_context(self, request):
        """Add load manager URL to admin context"""
        context = super().each_context(request)
        context['load_manager_url'] = reverse('load_dashboard')
        return context

# Create a custom admin class for the LoadManager model that links to the load dashboard
class LoadManagerAdmin(admin.ModelAdmin):
    list_display = ('name', 'view_dashboard_link')
    search_fields = ('name',)
    
    def view_dashboard_link(self, obj):
        """Add a link to the load dashboard"""
        url = reverse('load_dashboard')
        return format_html('<a href="{}" class="button">View Dashboard</a>', url)
    
    view_dashboard_link.short_description = "Dashboard"
    
    def has_add_permission(self, request):
        """Prevent adding new instances"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deleting instances"""
        return False
    
    def get_urls(self):
        from django.urls import path
        from chatbot_website.load_views import load_dashboard
        
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', load_dashboard, name='admin_load_dashboard'),
        ]
        return custom_urls + urls

# Register the LoadManager model with our custom admin
admin.site.register(LoadManager, LoadManagerAdmin)

# Register a function to modify admin index
def add_load_manager_link(sender, **kwargs):
    """Add load manager link to admin index template"""
    from django.contrib.admin.sites import AdminSite
    
    original_index = AdminSite.index
    
    def index_with_load_manager(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}
        extra_context['load_manager_url'] = reverse('load_dashboard')
        return original_index(self, request, extra_context)
    
    AdminSite.index = index_with_load_manager

# Connect the signal
from django.apps import apps
if apps.ready:
    add_load_manager_link(None) 