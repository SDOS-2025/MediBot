# chatbot/backends.py

from django.contrib.auth.backends import ModelBackend
from chatbot.models import CustomUser  # adjust if needed

class UIDAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Admin login form uses 'username', but your model has 'uid'
            user = CustomUser.objects.get(uid=username)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except CustomUser.DoesNotExist:
            return None
