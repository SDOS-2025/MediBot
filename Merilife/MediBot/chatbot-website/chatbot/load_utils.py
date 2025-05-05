from chatbot_website.load_manager import load_manager

def check_system_load():
    """
    Check the current system load and determine if the request can be processed.
    Returns:
        tuple: (can_proceed, message, server)
    """
    accepted, server = load_manager.register_connection()
    
    if not accepted:
        return False, "The system is currently experiencing high load. Please try again later.", None
    
    return True, "Request accepted", server

def release_server_connection(server):
    """Release the connection when processing is complete"""
    if server:
        load_manager.release_connection(server) 