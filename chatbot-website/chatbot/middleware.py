from django.shortcuts import redirect
class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.allowed_paths = ['/login/', '/register/', '/admin/']

    def __call__(self, request):
        if not request.user.is_authenticated and request.path not in self.allowed_paths:
            return redirect('login')
        return self.get_response(request)