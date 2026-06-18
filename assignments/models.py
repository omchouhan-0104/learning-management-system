"""
Assignments Models
Topics: ForeignKey, FileField, ORM
"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class Assignment(models.Model):
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    due_date = models.DateTimeField()
    total_marks = models.PositiveIntegerField(default=100)
    file = models.FileField(upload_to='assignments/questions/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    @property
    def is_overdue(self):
        return timezone.now() > self.due_date

    @property
    def submission_count(self):
        return self.submissions.count()


class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assignment_submissions'
    )
    file = models.FileField(upload_to='assignments/submissions/%Y/%m/')
    remarks = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_graded = models.BooleanField(default=False)
    marks_obtained = models.PositiveIntegerField(null=True, blank=True)
    teacher_feedback = models.TextField(blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ['assignment', 'student']
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"

    @property
    def percentage(self):
        if self.marks_obtained is not None and self.assignment.total_marks > 0:
            return round((self.marks_obtained / self.assignment.total_marks) * 100, 1)
        return None
