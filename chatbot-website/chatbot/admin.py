from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from chatbot.models import CustomUser

class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('uid', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff')}),  # Removed is_superuser
        ('Important dates', {'fields': ('date_joined',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('uid', 'password1', 'password2'),
        }),
    )
    list_display = ('uid', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_active')  # Removed groups and is_superuser
    search_fields = ('uid',)
    ordering = ('uid',)
    filter_horizontal = ()  # Removed groups and user_permissions

admin.site.register(CustomUser, CustomUserAdmin)