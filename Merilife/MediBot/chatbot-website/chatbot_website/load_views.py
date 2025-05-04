from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from .load_manager import load_manager

@staff_member_required
def load_dashboard(request):
    """Dashboard view for monitoring load manager status"""
    context = {
        'active_connections': load_manager.active_connections,
        'max_connections': load_manager.max_connections,
        'server_instances': load_manager.server_instances,
        'instance_load': load_manager.instance_load,
        'system_load': load_manager.get_system_load(),
        'is_overloaded': load_manager.is_system_overloaded(),
    }
    return render(request, 'load_dashboard.html', context)

def load_status_api(request):
    """API endpoint for getting current load status"""
    data = {
        'active_connections': load_manager.active_connections,
        'max_connections': load_manager.max_connections,
        'system_load_percent': load_manager.get_system_load(),
        'is_overloaded': load_manager.is_system_overloaded(),
        'server_status': {
            server: load_manager.instance_load[server] 
            for server in load_manager.server_instances
        }
    }
    return JsonResponse(data) 