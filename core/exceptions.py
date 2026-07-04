import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


def rtf_academy_exception_handler(exc, context):
    """
    Global exception handler that guarantees all API errors are formatted as JSON.
    """
    response = exception_handler(exc, context)

    if response is None:
        logger.error(f" CRITICAL 500 ERROR in {context['view'].__class__.__name__}: {str(exc)}", exc_info=True)

        return Response({
            "error": "Internal Server Error",
            "message": "The server encountered an unexpected condition. Our engineering team has been notified.",
            "status_code": 500
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    standardized_data = {
        "error": response.status_text if hasattr(response, 'status_text') else "API Error",
        "message": str(exc),
        "details": response.data,
        "status_code": response.status_code
    }

    response.data = standardized_data
    return response