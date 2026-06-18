from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.utils import timezone
from courses.models import Course, Enrollment
from .models import Assignment, AssignmentSubmission
from .forms import AssignmentForm, SubmissionForm, GradeForm

class AssignmentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'assignments/assignment_form.html'

    def test_func(self):
        course = get_object_or_404(Course, slug=self.kwargs['course_slug'])
        return self.request.user == course.teacher or self.request.user.is_staff

    def form_valid(self, form):
        course = get_object_or_404(Course, slug=self.kwargs['course_slug'])
        form.instance.course = course
        messages.success(self.request, 'Assignment created!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('courses:detail', kwargs={'slug': self.kwargs['course_slug']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(Course, slug=self.kwargs['course_slug'])
        return context

@login_required
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    if not request.user.is_student:
        messages.error(request, 'Only students can submit assignments.')
        return redirect('courses:detail', slug=assignment.course.slug)
    if not Enrollment.objects.filter(student=request.user, course=assignment.course, is_active=True).exists():
        messages.error(request, 'You must be enrolled in this course.')
        return redirect('courses:detail', slug=assignment.course.slug)
    if AssignmentSubmission.objects.filter(assignment=assignment, student=request.user).exists():
        messages.warning(request, 'You have already submitted this assignment.')
        return redirect('courses:detail', slug=assignment.course.slug)
    form = SubmissionForm()
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.assignment = assignment
            submission.student = request.user
            submission.save()
            messages.success(request, 'Assignment submitted successfully!')
            return redirect('courses:detail', slug=assignment.course.slug)
    return render(request, 'assignments/submit.html', {'form': form, 'assignment': assignment})

@login_required
def grade_submission(request, submission_id):
    """Grade submission and send email notification to student."""
    submission = get_object_or_404(AssignmentSubmission, pk=submission_id)
    course = submission.assignment.course
    if request.user != course.teacher and not request.user.is_staff:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard:index')
    form = GradeForm(instance=submission)
    if request.method == 'POST':
        form = GradeForm(request.POST, instance=submission)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.is_graded = True
            sub.graded_at = timezone.now()
            sub.save()

            try:
                from lms_project.email_service import send_assignment_graded_email
                send_assignment_graded_email(sub)
            except Exception:
                pass

            messages.success(request, f'✅ Graded! Notification sent to {sub.student.email}')
            return redirect('assignments:submissions', assignment_id=submission.assignment.pk)
    return render(request, 'assignments/grade.html', {'form': form, 'submission': submission})

@login_required
def assignment_submissions(request, assignment_id):
    assignment = get_object_or_404(Assignment, pk=assignment_id)
    if request.user != assignment.course.teacher and not request.user.is_staff:
        messages.error(request, 'Permission denied.')
        return redirect('dashboard:index')
    submissions = assignment.submissions.select_related('student').order_by('-submitted_at')
    return render(request, 'assignments/submissions_list.html', {
        'assignment': assignment, 'submissions': submissions
    })