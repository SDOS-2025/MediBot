from django.http import HttpResponse
from django.conf import settings
from .load_manager import load_manager
import logging

logger = logging.getLogger(__name__)

class LoadManagerMiddleware:
    """
    Middleware to handle load management for incoming requests.
    This helps prevent system overload by tracking and limiting concurrent connections.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Skip load management if disabled or for certain paths
        if not getattr(settings, 'LOAD_MANAGER_ENABLED', False):
            return self.get_response(request)
            
        # Skip load management for admin, static, and media requests
        path = request.path.lstrip('/')
        exempt_paths = ['admin/', 'static/', 'media/']
        if any(path.startswith(exempt) for exempt in exempt_paths):
            return self.get_response(request)
        
        # Check if system can handle this request
        accepted, server = load_manager.register_connection()
        
        if not accepted:
            logger.warning("Request rejected due to system overload")
            return HttpResponse("System is currently experiencing high load. Please try again later.", 
                              status=503)  # 503 Service Unavailable
        
        try:
            # Process the request
            response = self.get_response(request)
            return response
            
        finally:
            # Always release the connection when done
            if server:
                load_manager.release_connection(server)
                
        return self.get_response(request) 