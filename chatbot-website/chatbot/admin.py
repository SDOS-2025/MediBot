from django.contrib import admin
from .models import UserInteraction, Appointment

admin.site.register(UserInteraction)
admin.site.register(Appointment)