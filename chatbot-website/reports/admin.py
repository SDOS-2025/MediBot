from django.contrib import admin
from .models import UserInteraction, AppointmentReport

admin.site.register(UserInteraction)
admin.site.register(AppointmentReport)