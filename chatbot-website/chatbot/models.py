from django.db import models

class UserInteraction(models.Model):
    user_id = models.CharField(max_length=255)
    session_id = models.CharField(max_length=255)
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Interaction {self.id} - User: {self.user_id} - Session: {self.session_id}"

class Appointment(models.Model):
    user_id = models.CharField(max_length=255)
    appointment_date = models.DateTimeField()
    symptoms = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appointment {self.id} - User: {self.user_id} - Date: {self.appointment_date}"