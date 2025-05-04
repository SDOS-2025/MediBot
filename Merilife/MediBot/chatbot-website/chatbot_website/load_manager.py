import threading
import logging
import random
import time
from django.conf import settings

logger = logging.getLogger(__name__)

class LoadManager:
    """
    Load Manager that handles distribution of chatbot requests
    to maintain optimal system performance.
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(LoadManager, cls).__new__(cls)
                cls._instance.initialize()
            return cls._instance
    
    def initialize(self):
        """Initialize load manager state"""
        self.active_connections = 0
        self.max_connections = getattr(settings, 'LOAD_MANAGER_MAX_CONNECTIONS', 100)
        self.server_instances = ['server-1', 'server-2', 'server-3']  # Mock server instances
        self.instance_load = {server: 0 for server in self.server_instances}
        logger.info("Load Manager initialized with %d max connections", self.max_connections)
    
    def get_server_instance(self):
        """
        Select a server instance based on current load.
        Returns the server with the lowest load.
        """
        # Simple load balancing - choose server with lowest load
        return min(self.instance_load, key=self.instance_load.get)
    
    def register_connection(self):
        """Register a new connection and return success status"""
        with self._lock:
            if self.active_connections < self.max_connections:
                self.active_connections += 1
                chosen_server = self.get_server_instance()
                self.instance_load[chosen_server] += 1
                logger.debug("New connection registered. Total: %d", self.active_connections)
                return True, chosen_server
            else:
                logger.warning("Connection rejected. System at capacity: %d/%d", 
                              self.active_connections, self.max_connections)
                return False, None
    
    def release_connection(self, server_instance):
        """Release a connection when done"""
        with self._lock:
            if server_instance in self.instance_load:
                self.instance_load[server_instance] -= 1
                self.active_connections -= 1
                logger.debug("Connection released. Total: %d", self.active_connections)
    
    def get_system_load(self):
        """Return current system load as a percentage"""
        return (self.active_connections / self.max_connections) * 100
    
    def is_system_overloaded(self):
        """Check if system is overloaded (over 80% capacity)"""
        return self.get_system_load() > 80

# Singleton instance to be used across the application
load_manager = LoadManager() 