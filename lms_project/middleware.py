"""
Custom Middleware
Covers: Middleware, Request logging, Role tracking
"""
import logging
import time
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone

logger = logging.getLogger(__name__)


class RequestLogMiddleware(MiddlewareMixin):
    """
    Logs every request: method, path, user, response time.
    Topic: Custom Middleware
    """
    def process_request(self, request):
        request._start_time = time.time()

    def process_response(self, request, response):
        duration = time.time() - getattr(request, '_start_time', time.time())
        user = getattr(request, 'user', None)
        username = user.username if user and user.is_authenticated else 'anonymous'
        logger.info(
            f"[{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}] "
            f"{request.method} {request.path} | "
            f"User: {username} | "
            f"Status: {response.status_code} | "
            f"Time: {duration:.3f}s"
        )
        return response


class RoleMiddleware(MiddlewareMixin):
    """
    Attaches role info to request for easy access in views/templates.
    Topic: Middleware, Role-based access
    """
    def process_request(self, request):
        if request.user.is_authenticated:
            request.user_role = getattr(request.user, 'role', 'student')
            request.is_super_admin = request.user.is_superuser
            request.is_admin = request.user.is_staff and not request.user.is_superuser
            request.is_teacher = getattr(request.user, 'role', '') == 'teacher'
            request.is_student = getattr(request.user, 'role', '') == 'student'
        else:
            request.user_role = None
            request.is_super_admin = False
            request.is_admin = False
            request.is_teacher = False
            request.is_student = False
