from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Sum, Q
from django.utils import timezone

@login_required
def index(request):
    user = request.user
    if user.is_superuser or user.role == 'super_admin':
        return redirect('dashboard:super_admin')
    elif user.role == 'admin' or user.is_staff:
        return redirect('dashboard:admin_dashboard')
    elif user.role == 'teacher':
        return redirect('dashboard:teacher')
    else:
        return redirect('dashboard:student')

@login_required
def student_dashboard(request):
    if not (request.user.is_student or request.user.role == 'student'):
        return redirect('dashboard:index')

    from courses.models import Enrollment, Course
    from assignments.models import AssignmentSubmission
    from quizzes.models import QuizAttempt

    enrollments = Enrollment.objects.filter(
        student=request.user, is_active=True
    ).select_related('course', 'course__teacher')

    quiz_stats = QuizAttempt.objects.filter(student=request.user).aggregate(
        total=Count('id'),
        avg_score=Avg('percentage'),
        passed=Count('id', filter=Q(passed=True))
    )

    recent_submissions = AssignmentSubmission.objects.filter(
        student=request.user
    ).select_related('assignment', 'assignment__course').order_by('-submitted_at')[:5]

    pending_assignments = []
    for enrollment in enrollments:
        course = enrollment.course
        submitted_ids = AssignmentSubmission.objects.filter(
            student=request.user, assignment__course=course
        ).values_list('assignment_id', flat=True)
        pending = course.assignments.filter(
            due_date__gt=timezone.now()
        ).exclude(id__in=submitted_ids)
        pending_assignments.extend(pending)

    context = {
        'enrollments': enrollments,
        'quiz_stats': quiz_stats,
        'recent_submissions': recent_submissions,
        'pending_assignments': pending_assignments[:5],
        'total_enrolled': enrollments.count(),
    }
    return render(request, 'dashboard/student.html', context)

@login_required
def teacher_dashboard(request):
    if not (request.user.is_teacher or request.user.is_staff):
        return redirect('dashboard:index')

    from courses.models import Course, Enrollment
    from assignments.models import AssignmentSubmission

    courses = Course.objects.filter(teacher=request.user).annotate(
        student_count=Count('enrollments', distinct=True),
        assignment_count=Count('assignments', distinct=True),
        quiz_count=Count('quizzes', distinct=True),
    )

    total_students = Enrollment.objects.filter(
        course__teacher=request.user, is_active=True
    ).values('student').distinct().count()

    pending_grading = AssignmentSubmission.objects.filter(
        assignment__course__teacher=request.user,
        is_graded=False
    ).select_related('student', 'assignment', 'assignment__course')[:10]

    context = {
        'courses': courses,
        'total_students': total_students,
        'pending_grading': pending_grading,
        'total_courses': courses.count(),
        'published_courses': courses.filter(status='published').count(),
    }
    return render(request, 'dashboard/teacher.html', context)

@login_required
def admin_dashboard(request):
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('dashboard:index')

    from accounts.models import User
    from courses.models import Course, Enrollment
    from assignments.models import AssignmentSubmission
    from quizzes.models import QuizAttempt

    stats = {
        'total_users': User.objects.count(),
        'total_students': User.objects.filter(role='student').count(),
        'total_teachers': User.objects.filter(role='teacher').count(),
        'total_courses': Course.objects.count(),
        'published_courses': Course.objects.filter(status='published').count(),
        'total_enrollments': Enrollment.objects.filter(is_active=True).count(),
        'total_submissions': AssignmentSubmission.objects.count(),
        'total_quiz_attempts': QuizAttempt.objects.count(),
    }

    recent_users = User.objects.order_by('-created_at')[:5]
    recent_courses = Course.objects.select_related('teacher').order_by('-created_at')[:5]

    context = {
        'stats': stats,
        'recent_users': recent_users,
        'recent_courses': recent_courses,
    }
    return render(request, 'dashboard/admin.html', context)


@login_required
def super_admin_dashboard(request):
    if not (request.user.is_superuser or request.user.role == 'super_admin'):
        return redirect('dashboard:index')
    return admin_dashboard(request)
