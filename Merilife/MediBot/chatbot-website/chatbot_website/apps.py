from django.apps import AppConfig

class ChatbotWebsiteConfig(AppConfig):
    name = 'chatbot_website'
    verbose_name = 'Chatbot Website'

    def ready(self):
        # Register admin customizations when the app is ready
        from django.contrib.admin.sites import site
        from django.urls import reverse
        from django.utils.html import format_html
        
        # Add custom admin links
        def custom_admin_index(request, extra_context=None):
            if extra_context is None:
                extra_context = {}
            
            # Add the load manager URL to the admin context
            extra_context['has_load_manager'] = True
            extra_context['load_manager_url'] = reverse('load_dashboard')
            
            # Call the original index view
            return site.__class__.index(site, request, extra_context) 