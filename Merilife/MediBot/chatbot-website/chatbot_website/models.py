from django.db import models

class LoadManager(models.Model):
    """Dummy model for the Load Manager admin interface."""
    
    name = models.CharField(max_length=100, default="System Load Manager")
    
    class Meta:
        verbose_name = "Load Manager"
        verbose_name_plural = "Load Manager"
        
    def __str__(self):
        return self.name 