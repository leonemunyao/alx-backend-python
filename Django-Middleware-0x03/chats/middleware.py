import logging
from datetime import datetime
import os
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone


class RequestLoggingMiddleware:
    """
    Middleware to log user requests to a file.
    """

    def __init__(self, get_response):
        """Initialize the middleware.
        get_response is a callable that takes a request and returns a response.
        """
        self.get_response = get_response

        # Setting up logging configuration
        log_file_path = os.path.join(settings.BASE_DIR, 'chats', 'requests.log')

        # Configure the logger
        self.logger = logging.getLogger('request_logger')
        self.logger.setLevel(logging.INFO)

        # Create file handler if it doen't already exist
        if not self.logger.handlers:
            file_handler = logging.FileHandler(log_file_path)
            file_handler.setLevel(logging.INFO)

            # Create a formatter and set it for the handler
            formatter = logging.Formatter('%(message)s')
            file_handler.setFormatter(formatter)

            # Add the handler to the logger
            self.logger.addHandler(file_handler)

    def __call__(self, request):
        """Process the request ansd log the information. This method is called for each request."""

        # Get the user information
        user = request.user.username if request.user.is_authenticated else 'Anonymous'
        # Log the request details
        log_message = f"{datetime.now()} - User: {user} - Path: {request.path}"

        self.logger.info(log_message)

        response = self.get_response(request)

        return response
    

class RestrictAccessByTimeMiddleware:
    """Middleware to restrict access to chat endpoint during certain hours."""

    def __init__(self, get_response):
        """Initialize  the middleware.
        get_response is a callable that takes a request and returns a response.
        """

        self.get_response = get_response

        # Define the restricted hours.
        self.start_hour = 6  # 6 AM
        self.end_hour = 21   # 9 PM

        # Define which paths to be restricted
        self.restricted_paths = [
            '/api/conversations/',
            '/api/messages/',
            '/api/chats/',
            ]

    def __call__(self, request):
        """Check if the request is within restricted hours and path."""

        # Get the current server time
        current_time = timezone.now()
        current_hour = current_time.hour

        # Check if the request path should be restricted
        if self.should_restrict_path(request.path):
            # Check if the current hour is within the restricted range
            if self.start_hour <= current_hour < self.end_hour:
                return JsonResponse(
                    {'error': 'Access to this endpoint is restricted during this time.'},
                    status=403
                )
        # If not restricted, proceed with the request
        response = self.get_response(request)
        return response
    
    def should_restrict_path(self, path):
        """Check if the request path is in the restricted paths."""
        return any(path.startswith(restricted_path) for restricted_path in self.restricted_paths)
    

