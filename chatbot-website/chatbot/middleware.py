from django.shortcuts import redirect
from django.conf import settings

class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_paths = [
            '/login/',
            '/register/',
            '/admin/',
            '/pdf-preview/',
            '/generate-pdf/',
            '/media/'  # Keep this
        ]

    def __call__(self, request):
        # Allow all paths under /media/
        print(f"Processing path: {request.path}") 
        if request.path.startswith(settings.MEDIA_URL) or \
           request.path in ['/pdf-preview/', '/generate-pdf/']:
            return self.get_response(request)
            
        if hasattr(request, 'user') and \
           not request.user.is_authenticated and \
           request.path not in self.allowed_paths:
            return redirect('login')
        return self.get_response(request)