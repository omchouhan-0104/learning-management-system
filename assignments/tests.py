from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from courses.models import Course, Enrollment
from .models import Assignment, AssignmentSubmission

User = get_user_model()


class AssignmentTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher = User.objects.create_user(username='teacher', email='t@t.com', password='pass', role='teacher')
        self.student = User.objects.create_user(username='student', email='s@s.com', password='pass', role='student')
        self.course = Course.objects.create(
            title='Course', description='desc', teacher=self.teacher,
            status='published', level='beginner', is_free=True
        )
        Enrollment.objects.create(student=self.student, course=self.course, is_active=True)
        self.assignment = Assignment.objects.create(
            course=self.course, title='Test Assignment',
            description='Do this', due_date=timezone.now() + timedelta(days=7),
            total_marks=100
        )

    def test_assignment_str(self):
        self.assertIn('Test Assignment', str(self.assignment))

    def test_assignment_not_overdue(self):
        self.assertFalse(self.assignment.is_overdue)

    def test_overdue_assignment(self):
        self.assignment.due_date = timezone.now() - timedelta(days=1)
        self.assignment.save()
        self.assertTrue(self.assignment.is_overdue)

    def test_submission_percentage(self):
        sub = AssignmentSubmission(assignment=self.assignment, student=self.student, marks_obtained=80)
        self.assertEqual(sub.percentage, 80.0)
