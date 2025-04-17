from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.template.response import TemplateResponse
from django.urls import path
from chatbot.models import CustomUser, DoctorProfile, PatientProfile

class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('uid', 'password')}),
        ('Personal Information', {'fields': ('full_name', 'email', 'phone')}),
        ('Doctor Details', {
            'fields': ('specialization', 'qualification', 'bio'),
            'classes': ('collapse',),
        }),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('date_joined',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('uid', 'password1', 'password2', 'full_name', 'is_staff'),
        }),
    )
    list_display = ('uid', 'full_name', 'is_staff', 'specialization', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'specialization')
    search_fields = ('uid', 'full_name', 'email', 'specialization')
    ordering = ('uid',)

class CustomAdminSite(admin.AdminSite):
    site_header = 'Medico Administration'
    site_title = 'Medico Admin Portal'
    index_title = 'Administration'
    
    def get_urls(self):
        urls = super().get_urls()
        return urls
    
    def index(self, request, extra_context=None):
        # Get statistics for the dashboard
        doctor_count = CustomUser.objects.filter(is_staff=True).count()
        user_count = CustomUser.objects.filter(is_staff=False).count()
        chat_count = 0  # You can add actual chat count if you have a Chat model
        
        context = {
            'doctor_count': doctor_count,
            'user_count': user_count,
            'chat_count': chat_count,
        }
        
        if extra_context is not None:
            context.update(extra_context)
        
        return super().index(request, context)

# Create an instance of the custom admin site
admin_site = CustomAdminSite(name='customadmin')

# Register your models with the custom admin site
admin_site.register(CustomUser, CustomUserAdmin)

# Register with the default admin site as well (for compatibility)
admin.site.register(CustomUser, CustomUserAdmin)

# Register profiles
admin.site.register(DoctorProfile)
admin.site.register(PatientProfile)