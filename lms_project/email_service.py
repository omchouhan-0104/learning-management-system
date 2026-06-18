"""
Email Service — central place for all LMS emails
Handles: welcome email, email confirmation, enrollment confirmation,
         course invoice, assignment graded notification, admin alerts
"""
import logging
import uuid
from datetime import datetime

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone

logger = logging.getLogger(__name__)


def _base_context(recipient_email):
    """Shared context injected into every email template."""
    return {
        'site_url': getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000'),
        'site_name': getattr(settings, 'SITE_NAME', 'EduLearn LMS'),
        'recipient_email': recipient_email,
        'year': datetime.now().year,
    }


def send_html_email(subject, template_name, context, recipient_email):
    """
    Core helper — renders an HTML template and sends via SMTP.
    Falls back gracefully if email is not configured.
    """
    context.update(_base_context(recipient_email))
    try:
        html_content = render_to_string(template_name, context)
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send(fail_silently=False)
        logger.info(f"[EMAIL] Sent '{subject}' to {recipient_email}")
        return True
    except Exception as e:
        logger.error(f"[EMAIL] Failed to send '{subject}' to {recipient_email}: {e}")
        return False


# ─── 1. Welcome Email (Student) ────────────────────────────────────────────────

def send_welcome_student_email(user):
    """
    Sent when a new STUDENT registers or is created by admin.
    """
    return send_html_email(
        subject=f'🎓 Welcome to EduLearn LMS, {user.first_name}!',
        template_name='emails/welcome_student.html',
        context={'user': user},
        recipient_email=user.email,
    )


# ─── 2. Welcome Email (Teacher) ────────────────────────────────────────────────

def send_welcome_teacher_email(user):
    """
    Sent when a new TEACHER account is created.
    """
    return send_html_email(
        subject=f'👨‍🏫 Your Teacher Account on EduLearn LMS is Ready!',
        template_name='emails/welcome_teacher.html',
        context={'user': user},
        recipient_email=user.email,
    )


# ─── 3. Email Confirmation (Verify Email) ──────────────────────────────────────

def send_confirm_email(user, token):
    """
    Sent after registration — user must click link to verify email.
    token: a signed UUID stored in EmailConfirmation model
    """
    site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
    verify_url = f"{site_url}/accounts/verify-email/{token}/"
    return send_html_email(
        subject='✅ Please Verify Your EduLearn Email Address',
        template_name='emails/confirm_email.html',
        context={'user': user, 'verify_url': verify_url},
        recipient_email=user.email,
    )


# ─── 4. Enrollment Confirmation (Free Course) ──────────────────────────────────

def send_enrollment_confirmation_email(user, course, enrollment):
    """
    Sent when a student enrolls in a FREE course.
    """
    return send_html_email(
        subject=f'📚 Enrolled: {course.title}',
        template_name='emails/enrollment_confirmation.html',
        context={
            'user': user,
            'course': course,
            'enrollment': enrollment,
            'enrolled_on': enrollment.enrolled_at.strftime('%B %d, %Y'),
        },
        recipient_email=user.email,
    )


# ─── 5. Course Invoice (Paid Course) ───────────────────────────────────────────

def send_course_invoice_email(user, course, enrollment):
    """
    Sent when a student purchases a PAID course.
    Generates an invoice number and attaches all purchase details.
    """
    invoice_number = f"INV-{timezone.now().strftime('%Y%m')}-{str(uuid.uuid4())[:8].upper()}"
    invoice_date = timezone.now().strftime('%B %d, %Y')

    return send_html_email(
        subject=f'🧾 Invoice for {course.title} – EduLearn LMS',
        template_name='emails/course_invoice.html',
        context={
            'user': user,
            'course': course,
            'enrollment': enrollment,
            'invoice_number': invoice_number,
            'invoice_date': invoice_date,
        },
        recipient_email=user.email,
    )


# ─── 6. Admin Notification — New User Registered ───────────────────────────────

def send_new_user_admin_notification(new_user):
    """
    Notifies all admins/superadmins when a new user registers.
    """
    from accounts.models import User
    admins = User.objects.filter(
        role__in=['admin', 'super_admin'],
        is_active=True,
        is_staff=True,
    ).exclude(email='')

    results = []
    for admin in admins:
        ok = send_html_email(
            subject=f'🔔 New User Registered: {new_user.get_full_name()} ({new_user.get_role_display()})',
            template_name='emails/new_user_admin_notify.html',
            context={'new_user': new_user},
            recipient_email=admin.email,
        )
        results.append(ok)
    return all(results)


# ─── 7. Assignment Graded Notification ─────────────────────────────────────────

def send_assignment_graded_email(submission):
    """
    Notifies the student when their assignment has been graded.
    """
    return send_html_email(
        subject=f'📝 Your Assignment Has Been Graded – {submission.assignment.title}',
        template_name='emails/assignment_graded.html',
        context={
            'user': submission.student,
            'submission': submission,
        },
        recipient_email=submission.student.email,
    )
