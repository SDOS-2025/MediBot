from django.db import models
from django.conf import settings

class UserInteraction(models.Model):
    user_id = models.CharField(max_length=255)
    interaction_text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Interaction {self.id} by User {self.user_id} at {self.timestamp}"

class AppointmentReport(models.Model):
    user_interaction = models.ForeignKey(UserInteraction, on_delete=models.CASCADE)
    report_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Report {self.id} for Interaction {self.user_interaction.id}"

class Report(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reports_generated_for',
        limit_choices_to={'is_staff': False}
    )
    assigned_doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_reports',
        limit_choices_to={'is_staff': True}
    )

    def __str__(self):
        return self.title