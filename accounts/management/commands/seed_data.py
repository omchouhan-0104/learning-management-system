"""
Custom Management Command: seed_data
Topic: Custom Management Commands
Usage: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = 'Seeds the database with demo users, groups, courses, and sample data'

    def handle(self, *args, **options):
        from accounts.models import User
        from courses.models import Category, Course, Enrollment
        from assignments.models import Assignment
        from quizzes.models import Quiz, Question, Option
        from django.utils import timezone
        from datetime import timedelta

        self.stdout.write(self.style.WARNING('🌱 Seeding demo data...'))

        # ── Groups ──────────────────────────────────────────────────────
        for g in ['Students', 'Teachers', 'Admins']:
            Group.objects.get_or_create(name=g)
        self.stdout.write('  ✅ Groups ready')

        # ── Users ────────────────────────────────────────────────────────
        # Always force-set password so it is guaranteed to be admin123
        users_spec = [
            dict(username='superadmin', email='superadmin@lms.com',
                 first_name='Super', last_name='Admin',
                 role='super_admin', is_superuser=True, is_staff=True),
            dict(username='admin1', email='admin1@lms.com',
                 first_name='Admin', last_name='User',
                 role='admin', is_superuser=False, is_staff=True),
            dict(username='teacher1', email='teacher1@lms.com',
                 first_name='Alice', last_name='Johnson',
                 role='teacher', is_superuser=False, is_staff=False),
            dict(username='teacher2', email='teacher2@lms.com',
                 first_name='Bob', last_name='Smith',
                 role='teacher', is_superuser=False, is_staff=False),
            dict(username='student1', email='student1@lms.com',
                 first_name='Charlie', last_name='Brown',
                 role='student', is_superuser=False, is_staff=False),
            dict(username='student2', email='student2@lms.com',
                 first_name='Diana', last_name='Prince',
                 role='student', is_superuser=False, is_staff=False),
            dict(username='student3', email='student3@lms.com',
                 first_name='Evan', last_name='Williams',
                 role='student', is_superuser=False, is_staff=False),
        ]

        created_users = {}
        for spec in users_spec:
            username = spec['username']
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': spec['email'],
                    'first_name': spec['first_name'],
                    'last_name': spec['last_name'],
                    'role': spec['role'],
                    'is_superuser': spec['is_superuser'],
                    'is_staff': spec['is_staff'],
                    'is_active': True,
                }
            )
            # Always reset password and flags (fixes stale data)
            user.set_password('admin123')
            user.is_active = True
            user.is_superuser = spec['is_superuser']
            user.is_staff = spec['is_staff']
            user.role = spec['role']
            user.save()
            tag = '✅ Created' if created else '🔄 Updated'
            self.stdout.write(f'  {tag}: {username} ({spec["role"]}) — password: admin123')
            created_users[username] = user

        # ── Categories ───────────────────────────────────────────────────
        cats = [
            ('Python Programming', 'python-programming'),
            ('Web Development', 'web-development'),
            ('Data Science', 'data-science'),
            ('Django Framework', 'django-framework'),
        ]
        categories = {}
        for name, slug in cats:
            cat, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name})
            categories[slug] = cat

        # ── Courses ───────────────────────────────────────────────────────
        t1 = created_users['teacher1']
        t2 = created_users['teacher2']

        courses_spec = [
            dict(title='Python for Beginners',
                 description='Learn Python from scratch. Variables, loops, functions, OOP, and file handling.',
                 category=categories['python-programming'], teacher=t1,
                 status='published', level='beginner', is_free=True, price=0),
            dict(title='Django Web Development',
                 description='Build full-stack web apps with Django. Models, views, templates, auth, ORM, admin.',
                 category=categories['django-framework'], teacher=t1,
                 status='published', level='intermediate', is_free=False, price=999),
            dict(title='Data Science with Python',
                 description='Data analysis and visualization using pandas, matplotlib, and seaborn.',
                 category=categories['data-science'], teacher=t2,
                 status='published', level='intermediate', is_free=True, price=0),
            dict(title='Advanced Django REST APIs',
                 description='Build production-ready REST APIs with Django.',
                 category=categories['web-development'], teacher=t2,
                 status='draft', level='advanced', is_free=False, price=1499),
        ]
        created_courses = []
        for spec in courses_spec:
            course, created = Course.objects.get_or_create(
                title=spec['title'], defaults=spec
            )
            created_courses.append(course)
            tag = '✅' if created else '⏩'
            self.stdout.write(f'  {tag} Course: {course.title}')

        # ── Enrollments ───────────────────────────────────────────────────
        published = [c for c in created_courses if c.status == 'published']
        students = [created_users[u] for u in ['student1', 'student2', 'student3']]
        for student in students:
            for course in published[:2]:
                Enrollment.objects.get_or_create(
                    student=student, course=course,
                    defaults={'is_active': True, 'progress': 30}
                )
        self.stdout.write('  ✅ Enrollments ready')

        # ── Assignments ───────────────────────────────────────────────────
        if published:
            course = published[0]
            for i in range(1, 3):
                Assignment.objects.get_or_create(
                    title=f'Assignment {i}: {course.title[:30]}',
                    course=course,
                    defaults={
                        'description': f'Complete the exercises for module {i}.',
                        'due_date': timezone.now() + timedelta(days=7 * i),
                        'total_marks': 100,
                    }
                )
            self.stdout.write('  ✅ Assignments ready')

        # ── Quiz ──────────────────────────────────────────────────────────
        if published:
            course = published[0]
            quiz, created = Quiz.objects.get_or_create(
                title='Python Basics Quiz', course=course,
                defaults={'description': 'Test your Python fundamentals.',
                          'time_limit_minutes': 15, 'passing_score': 60}
            )
            if created:
                q_data = [
                    ("What is the output of print(type([]))?",
                     ["<class 'list'>", "<class 'tuple'>", "<class 'dict'>", "<class 'set'>"], 0),
                    ("Which keyword defines a function in Python?",
                     ['func', 'def', 'define', 'function'], 1),
                    ("Python is an interpreted language.",
                     ['True', 'False'], 0),
                ]
                for idx, (text, opts, correct_idx) in enumerate(q_data):
                    q = Question.objects.create(quiz=quiz, text=text, order=idx + 1, marks=1)
                    for j, opt_text in enumerate(opts):
                        Option.objects.create(question=q, text=opt_text, is_correct=(j == correct_idx))
            self.stdout.write('  ✅ Quiz ready')

        self.stdout.write(self.style.SUCCESS(
            '\n✨ Done! All accounts use password: admin123\n'
            '   superadmin / admin1 / teacher1 / teacher2 / student1 / student2 / student3'
        ))
