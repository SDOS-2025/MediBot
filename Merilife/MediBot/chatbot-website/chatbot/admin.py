from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.template.response import TemplateResponse
from django.urls import path, reverse
from chatbot.models import CustomUser, DoctorProfile, PatientProfile
from django.http import HttpResponseRedirect

# Add inline for DoctorProfile
class DoctorProfileInline(admin.StackedInline):
    model = DoctorProfile
    can_delete = False
    verbose_name_plural = 'Doctor Profile'

class CustomUserAdmin(UserAdmin):
    # Include DoctorProfile inline
    inlines = [DoctorProfileInline]

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
    list_display = ('uid', 'full_name', 'is_staff', 'get_specialization', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'doctor_profile__specialization')
    search_fields = ('uid', 'full_name', 'email', 'doctor_profile__specialization')
    ordering = ('uid',)

    def get_specialization(self, obj):
        # Display the specialization from the related DoctorProfile
        if hasattr(obj, 'doctor_profile') and obj.doctor_profile:
            return obj.doctor_profile.specialization
        return ''
    get_specialization.short_description = 'Specialization'

class CustomAdminSite(admin.AdminSite):
    site_header = 'Medico Administration'
    site_title = 'Medico Admin Portal'
    index_title = 'Administration'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('load-manager/', self.admin_view(self.load_manager_view), name='admin_load_manager'),
        ]
        return custom_urls + urls
    
    def load_manager_view(self, request):
        """Redirect to the load manager dashboard"""
        return HttpResponseRedirect(reverse('load_dashboard'))
    
    def index(self, request, extra_context=None):
        # Get statistics for the dashboard
        doctor_count = CustomUser.objects.filter(is_staff=True).count()
        user_count = CustomUser.objects.filter(is_staff=False).count()
        chat_count = 0  # You can add actual chat count if you have a Chat model
        
        # Add load manager link to the context
        context = {
            'doctor_count': doctor_count,
            'user_count': user_count,
            'chat_count': chat_count,
            'load_manager_url': reverse('load_dashboard'),
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

# Add a custom admin action to view the load manager dashboard
def view_load_manager(modeladmin, request, queryset):
    """View the load manager dashboard"""
    return HttpResponseRedirect(reverse('load_dashboard'))

view_load_manager.short_description = "View Load Manager Dashboard"

# Add this action to every admin
admin.site.add_action(view_load_manager, 'view_load_manager')