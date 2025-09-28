"""
Custom middleware classes for the Django messaging app.
"""
import logging
import time
from datetime import datetime
from django.http import HttpResponseForbidden
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from collections import defaultdict

# Configure logging
logging.basicConfig(
    filename='requests.log',
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware that logs each user's requests to a file, including timestamp, user, and request path.
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware.
        """
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        """
        Process the request and log information.
        """
        # Get user information
        user = getattr(request, 'user', None)
        user_info = user.email if user and user.is_authenticated else 'Anonymous'
        
        # Log the request
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"{timestamp} - User: {user_info} - Path: {request.path}"
        logger.info(log_message)
        
        # Continue processing the request
        response = self.get_response(request)
        return response


class RestrictAccessByTimeMiddleware(MiddlewareMixin):
    """
    Middleware that restricts access to the messaging app during certain hours.
    Access is denied outside 9 AM and 6 PM.
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware.
        """
        self.get_response = get_response
        super().__init__(get_response)
    
    def __call__(self, request):
        """
        Check the current time and deny access if outside allowed hours.
        """
        current_time = datetime.now().time()
        
        # Define allowed hours (9 AM to 6 PM)
        start_time = datetime.strptime('09:00', '%H:%M').time()
        end_time = datetime.strptime('18:00', '%H:%M').time()
        
        # Check if current time is outside allowed hours
        if not (start_time <= current_time <= end_time):
            return HttpResponseForbidden(
                "Access denied. The messaging system is only available between 9 AM and 6 PM."
            )
        
        # Continue processing if within allowed hours
        response = self.get_response(request)
        return response


class OffensiveLanguageMiddleware(MiddlewareMixin):
    """
    Middleware that limits the number of chat messages a user can send within a time window.
    Implements rate limiting based on IP address (5 messages per minute).
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware.
        """
        self.get_response = get_response
        super().__init__(get_response)
        # Use Django cache for storing IP request counts
        self.message_limit = 5  # messages per minute
        self.time_window = 60   # seconds
    
    def __call__(self, request):
        """
        Track POST requests (messages) from each IP and implement rate limiting.
        """
        # Only apply rate limiting to POST requests on message endpoints
        if request.method == 'POST' and '/api/messages/' in request.path:
            client_ip = self.get_client_ip(request)
            
            # Create cache key for this IP
            cache_key = f"message_count_{client_ip}"
            
            # Get current count for this IP
            current_count = cache.get(cache_key, 0)
            
            # Check if limit exceeded
            if current_count >= self.message_limit:
                return HttpResponseForbidden(
                    f"Rate limit exceeded. You can only send {self.message_limit} messages per minute."
                )
            
            # Increment counter
            cache.set(cache_key, current_count + 1, self.time_window)
        
        # Continue processing the request
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """
        Get the client's IP address from the request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RolepermissionMiddleware(MiddlewareMixin):  # Changed from RolePermissionMiddleware
    """
    Middleware that checks user roles before allowing access to specific actions.
    Only admin and moderator users can access certain endpoints.
    """
    
    def __init__(self, get_response):
        """
        Initialize the middleware.
        """
        self.get_response = get_response
        super().__init__(get_response)
        
        # Define protected endpoints that require admin/moderator access
        self.protected_paths = [
            '/api/admin/',
            '/api/users/',  # User management
            '/admin/',      # Django admin
        ]
        
        # Define allowed roles for protected endpoints
        self.allowed_roles = ['admin', 'host']  # Note: using 'host' as moderator equivalent
    
    def __call__(self, request):
        """
        Check user role before allowing access to protected endpoints.
        """
        # Check if the request path requires special permissions
        requires_permission = any(
            protected_path in request.path 
            for protected_path in self.protected_paths
        )
        
        if requires_permission:
            # Check if user is authenticated
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Authentication required for this action.")
            
            # Check if user has required role
            user_role = getattr(request.user, 'role', 'guest')
            if user_role not in self.allowed_roles:
                return HttpResponseForbidden(
                    f"Access denied. This action requires {' or '.join(self.allowed_roles)} role."
                )
        
        # Continue processing the request
        response = self.get_response(request)
        return response