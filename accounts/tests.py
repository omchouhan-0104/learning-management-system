from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTest(TestCase):

    def setUp(self):
        self.student = User.objects.create_user(
            username='teststudent', email='student@test.com',
            password='testpass123', role='student',
            first_name='Test', last_name='Student'
        )
        self.teacher = User.objects.create_user(
            username='testteacher', email='teacher@test.com',
            password='testpass123', role='teacher',
            first_name='Test', last_name='Teacher'
        )

    def test_user_str(self):
        self.assertIn('teststudent', str(self.student).lower() + self.student.username)

    def test_is_student_property(self):
        self.assertTrue(self.student.is_student)
        self.assertFalse(self.teacher.is_student)

    def test_is_teacher_property(self):
        self.assertTrue(self.teacher.is_teacher)
        self.assertFalse(self.student.is_teacher)

    def test_custom_manager_get_students(self):
        students = User.objects.get_students()
        self.assertIn(self.student, students)
        self.assertNotIn(self.teacher, students)

    def test_custom_manager_get_teachers(self):
        teachers = User.objects.get_teachers()
        self.assertIn(self.teacher, teachers)
        self.assertNotIn(self.student, teachers)

    def test_get_dashboard_url_student(self):
        self.assertEqual(self.student.get_dashboard_url(), '/dashboard/student/')

    def test_get_dashboard_url_teacher(self):
        self.assertEqual(self.teacher.get_dashboard_url(), '/dashboard/teacher/')


class AuthViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='loginuser', email='login@test.com',
            password='testpass123', role='student'
        )

    def test_login_page_loads(self):
        resp = self.client.get(reverse('accounts:login'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Sign in')

    def test_register_page_loads(self):
        resp = self.client.get(reverse('accounts:register'))
        self.assertEqual(resp.status_code, 200)

    def test_login_valid(self):
        resp = self.client.post(reverse('accounts:login'), {
            'username': 'loginuser', 'password': 'testpass123'
        })
        self.assertRedirects(resp, '/dashboard/student/')

    def test_login_invalid(self):
        resp = self.client.post(reverse('accounts:login'), {
            'username': 'loginuser', 'password': 'wrongpass'
        })
        self.assertEqual(resp.status_code, 200)

    def test_register_creates_user(self):
        resp = self.client.post(reverse('accounts:register'), {
            'username': 'newuser', 'first_name': 'New', 'last_name': 'User',
            'email': 'newuser@test.com', 'role': 'student',
            'password1': 'Django@secure1', 'password2': 'Django@secure1'
        })
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_profile_requires_login(self):
        resp = self.client.get(reverse('accounts:profile'))
        self.assertRedirects(resp, '/accounts/login/?next=/accounts/profile/')

    def test_profile_accessible_when_logged_in(self):
        self.client.login(username='loginuser', password='testpass123')
        resp = self.client.get(reverse('accounts:profile'))
        self.assertEqual(resp.status_code, 200)
