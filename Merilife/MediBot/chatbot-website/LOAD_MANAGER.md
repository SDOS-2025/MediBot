# Load Manager for MediBot Architecture

This document describes the load manager component that has been added to the MediBot architecture.

## Overview

The load manager is responsible for distributing and managing the system's workload across available server instances. It helps prevent system overload by tracking concurrent connections and distributing requests to the least loaded servers.

## Components

The load manager implementation consists of several components:

1. **Load Manager Class (`load_manager.py`)**:
   - Implemented as a singleton
   - Tracks active connections and server load
   - Provides methods for registering and releasing connections
   - Implements a basic load balancing strategy

2. **Load Manager Middleware (`load_middleware.py`)**:
   - Intercepts incoming requests
   - Applies load management policies
   - Returns appropriate responses when the system is overloaded

3. **Dashboard (`load_dashboard.html`)**:
   - Provides real-time visualization of system load
   - Displays active connections and server status
   - Accessible via the admin interface at `/admin/load/`

4. **API Endpoint (`load_views.py`)**:
   - Returns current load status as JSON
   - Used by the dashboard for real-time updates
   - Available at `/api/load-status/`

## Configuration

The load manager can be configured in `settings.py` with the following settings:

```python
# Load Manager Configuration
LOAD_MANAGER_MAX_CONNECTIONS = 100  # Maximum number of concurrent connections
LOAD_MANAGER_ENABLED = True         # Enable/disable load management
LOAD_MANAGER_TIMEOUT = 30           # Connection timeout in seconds
```

## Integration

The load manager is integrated into the chatbot's AI wrapper to manage the load of AI-related requests:

1. Before processing a request, the system checks if it can handle additional load
2. If the system is overloaded, it returns an appropriate message to the user
3. When processing is complete, the connection is released

## Example Usage

```python
from chatbot.utils import check_system_load, release_server_connection

def process_request(request_data):
    # Check system load first
    can_proceed, message, server = check_system_load()
    if not can_proceed:
        return message
    
    try:
        # Process the request
        result = do_something_with(request_data)
        return result
    finally:
        # Always release the connection when done
        release_server_connection(server)
```

## Dashboard Access

The load manager dashboard is accessible to staff members at `/admin/load/`. It provides:

- Current active connections
- System load percentage
- Status of individual server instances
- Auto-refreshing metrics

## Future Improvements

Potential enhancements for the load manager include:

1. More sophisticated load balancing algorithms
2. Persistent metrics and historical data
3. Automatic scaling of resources based on load
4. Predictive load management based on historical patterns
5. Integration with cloud infrastructure for dynamic scaling 