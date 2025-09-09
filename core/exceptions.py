"""
Custom exception handler to match API specification.
"""

from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    """
    Custom exception handler for standardized error responses.
    
    Returns error responses that match the API specification exactly.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Customize authentication errors (401)
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            custom_response_data = {
                'detail': 'Nicht authentifiziert.'
            }
            response.data = custom_response_data
        
        # Customize permission errors (403) 
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            custom_response_data = {
                'detail': 'Access denied.'
            }
            response.data = custom_response_data
        
        # Customize not found errors (404)
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            # For quiz endpoints, keep specific message
            if 'quiz' in str(context.get('view', '')).lower():
                custom_response_data = {
                    'detail': 'Quiz not found.'
                }
            else:
                custom_response_data = {
                    'detail': 'Not found.'
                }
            response.data = custom_response_data
        
        # Customize server errors (500)
        elif response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            custom_response_data = {
                'detail': 'Internal server error.'
            }
            response.data = custom_response_data

    return response
