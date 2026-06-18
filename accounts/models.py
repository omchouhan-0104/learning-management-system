from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
import uuid

class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'super_admin')
        return self.create_user(username, email, password, **extra_fields)

    def get_teachers(self):
        return self.filter(role='teacher', is_active=True)

    def get_students(self):
        return self.filter(role='student', is_active=True)

    def get_admins(self):
        return self.filter(role='admin', is_active=True)


class User(AbstractUser):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    @property
    def is_super_admin(self):
        return self.role == 'super_admin' or self.is_superuser

    @property
    def is_admin_user(self):
        return self.role == 'admin' or self.is_staff

    @property
    def is_teacher(self):
        return self.role == 'teacher'

    @property
    def is_student(self):
        return self.role == 'student'

    @property
    def profile_image_url(self):
        if self.profile_image:
            return self.profile_image.url
        return '/static/images/default_avatar.png'

    def get_dashboard_url(self):
        role_urls = {
            'super_admin': '/dashboard/super-admin/',
            'admin': '/dashboard/admin/',
            'teacher': '/dashboard/teacher/',
            'student': '/dashboard/student/',
        }
        return role_urls.get(self.role, '/dashboard/')


class EmailConfirmationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_token')
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"Token for {self.user.username}"
    @property
    def is_expired(self):
        from datetime import timedelta
        return timezone.now() > self.created_at + timedelta(hours=24)
