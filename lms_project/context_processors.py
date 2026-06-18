"""
Context Processors
Topic: Context Processors - inject data into ALL templates automatically
"""
from django.conf import settings


def site_settings(request):
    """
    Injects site-wide settings into every template context.
    Available as {{ SITE_NAME }}, {{ SITE_DESCRIPTION }} in all templates.
    """
    return {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'EduLearn LMS'),
        'SITE_DESCRIPTION': getattr(settings, 'SITE_DESCRIPTION', 'Learning Management System'),
        'DEBUG': settings.DEBUG,
    }


def user_notifications(request):
    """
    Injects notification counts for authenticated users.
    Available as {{ unread_notifications }} in all templates.
    """
    if not request.user.is_authenticated:
        return {'unread_notifications': 0, 'user_role': None}

    # Lazy imports to avoid circular dependency
    try:
        from assignments.models import AssignmentSubmission
        from quizzes.models import QuizAttempt

        unread_count = 0
        role = getattr(request.user, 'role', 'student')

        if role == 'teacher':
            # Pending submissions to grade
            from courses.models import Course
            teacher_courses = Course.objects.filter(teacher=request.user)
            unread_count = AssignmentSubmission.objects.filter(
                assignment__course__in=teacher_courses,
                is_graded=False
            ).count()

        elif role == 'student':
            # Ungraded submissions for student
            unread_count = AssignmentSubmission.objects.filter(
                student=request.user,
                is_graded=False
            ).count()

        return {
            'unread_notifications': unread_count,
            'user_role': role,
        }
    except Exception:
        return {'unread_notifications': 0, 'user_role': None}
