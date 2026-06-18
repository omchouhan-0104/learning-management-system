from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import User, EmailConfirmationToken

@receiver(post_save, sender=User)
def on_user_created(sender, instance, created, **kwargs):
    if not created:
        return
    role_group_map = {
        'student': 'Students',
        'teacher': 'Teachers',
        'admin': 'Admins',
    }
    group_name = role_group_map.get(instance.role)
    if group_name:
        group, _ = Group.objects.get_or_create(name=group_name)
        instance.groups.add(group)

    try:
        token_obj, _ = EmailConfirmationToken.objects.get_or_create(user=instance)
    except Exception:
        token_obj = None

    try:
        from lms_project.email_service import (
            send_welcome_student_email,
            send_welcome_teacher_email,
            send_confirm_email,
            send_new_user_admin_notification,
        )

        if instance.role == 'student':
            send_welcome_student_email(instance)
        elif instance.role == 'teacher':
            send_welcome_teacher_email(instance)

        if token_obj and instance.email:
            send_confirm_email(instance, str(token_obj.token))

        if instance.role in ('student', 'teacher'):
            send_new_user_admin_notification(instance)

    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Signal email error for {instance.username}: {e}")


@receiver(post_save, sender=User)
def set_staff_flag_for_admin(sender, instance, created, **kwargs):
    if instance.role == 'admin' and not instance.is_staff:
        User.objects.filter(pk=instance.pk).update(is_staff=True)


@receiver(pre_save, sender=User)
def normalize_email_signal(sender, instance, **kwargs):
    if instance.email:
        instance.email = instance.email.lower()
