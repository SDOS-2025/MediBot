from django.core.asgi import get_asgi_application
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_website.settings')

application = get_asgi_application()