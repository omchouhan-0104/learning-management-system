from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from courses.models import Course, Enrollment
from .models import Quiz, Question, Option, QuizAttempt

User = get_user_model()


class QuizTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.teacher = User.objects.create_user(username='teacher', email='t@t.com', password='pass', role='teacher')
        self.student = User.objects.create_user(username='student', email='s@s.com', password='pass', role='student')
        self.course = Course.objects.create(
            title='Quiz Course', description='desc', teacher=self.teacher,
            status='published', level='beginner', is_free=True
        )
        Enrollment.objects.create(student=self.student, course=self.course, is_active=True)
        self.quiz = Quiz.objects.create(
            course=self.course, title='Test Quiz',
            time_limit_minutes=10, passing_score=60
        )
        self.q1 = Question.objects.create(quiz=self.quiz, text='What is 2+2?', marks=1, order=1)
        self.opt_correct = Option.objects.create(question=self.q1, text='4', is_correct=True)
        self.opt_wrong = Option.objects.create(question=self.q1, text='5', is_correct=False)

    def test_quiz_str(self):
        self.assertIn('Test Quiz', str(self.quiz))

    def test_question_count(self):
        self.assertEqual(self.quiz.question_count, 1)

    def test_correct_answer(self):
        self.assertEqual(self.q1.correct_answer, self.opt_correct)

    def test_quiz_detail_view(self):
        self.client.login(username='student', password='pass')
        resp = self.client.get(reverse('quizzes:detail', kwargs={'pk': self.quiz.pk}))
        self.assertEqual(resp.status_code, 200)
