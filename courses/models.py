"""
Courses Models
Topics: ForeignKey, ManyToMany, FileField, ORM, Custom Managers,
        Model Validation, full_clean()
"""
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone


class Category(models.Model):
    """Course Category - Topic: ForeignKey target"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class CourseManager(models.Manager):
    """Custom Manager - Topic: Custom Managers"""
    def published(self):
        return self.filter(status='published')

    def by_teacher(self, teacher):
        return self.filter(teacher=teacher)

    def with_enrollment_count(self):
        """Topic: Annotation"""
        from django.db.models import Count
        return self.annotate(enrollment_count=Count('enrollments'))


class Course(models.Model):
    """
    Course Model
    Topics: ForeignKey, ManyToManyField, ImageField, Model Validation
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    LEVEL_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='courses'   # Topic: related_name
    )
    # Topic: ForeignKey Relationship
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='taught_courses',
        limit_choices_to={'role': 'teacher'}
    )
    # Topic: ManyToMany Relationship
    enrolled_students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Enrollment',
        related_name='enrolled_courses',
        blank=True
    )
    thumbnail = models.ImageField(upload_to='courses/thumbnails/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    duration_weeks = models.PositiveIntegerField(default=4)
    max_students = models.PositiveIntegerField(default=50)
    is_free = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    views = models.PositiveIntegerField(default=0)  # Used with F Expression
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CourseManager()  # Custom Manager

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('courses:detail', kwargs={'slug': self.slug})

    # Topic: Model Validation - full_clean()
    def clean(self):
        """Model-level validation called by full_clean()"""
        if not self.is_free and self.price <= 0:
            raise ValidationError({'price': 'Paid courses must have a price greater than 0.'})
        if self.max_students < 1:
            raise ValidationError({'max_students': 'Must allow at least 1 student.'})

    def save(self, *args, **kwargs):
        # Auto-generate slug
        if not self.slug:
            from django.utils.text import slugify
            base_slug = slugify(self.title)
            slug = base_slug
            n = 1
            while Course.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{n}"
                n += 1
            self.slug = slug
        self.full_clean()  # Topic: full_clean() triggers model validation
        super().save(*args, **kwargs)

    @property
    def enrollment_count(self):
        return self.enrollments.filter(is_active=True).count()

    @property
    def is_full(self):
        return self.enrollment_count >= self.max_students


class Enrollment(models.Model):
    """
    Through model for Course <-> Student ManyToMany
    Topic: ManyToMany through model
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress = models.PositiveIntegerField(default=0)  # 0-100

    class Meta:
        unique_together = ['student', 'course']  # One enrollment per student/course
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.student.username} → {self.course.title}"


class Note(models.Model):
    """
    Course Notes (downloadable files)
    Topics: FileField, MEDIA_ROOT, ForeignKey
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # Topic: FileField, MEDIA_ROOT
    file = models.FileField(upload_to='notes/%Y/%m/')
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    @property
    def file_extension(self):
        name = self.file.name
        return name.split('.')[-1].upper() if '.' in name else 'FILE'
