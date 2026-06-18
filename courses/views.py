"""
Courses Views — includes enrollment emails and invoice emails
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.http import FileResponse, Http404
from django.db.models import Q, F, Count, Avg

from .models import Course, Enrollment, Note, Category
from .forms import CourseForm, NoteForm


class CourseListView(ListView):
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 9

    def get_queryset(self):
        queryset = Course.objects.published().select_related('teacher', 'category')
        search = self.request.GET.get('search', '')
        category = self.request.GET.get('category', '')
        level = self.request.GET.get('level', '')
        is_free = self.request.GET.get('is_free', '')
        sort = self.request.GET.get('sort', '-created_at')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(teacher__first_name__icontains=search) |
                Q(category__name__icontains=search)
            )
        if category:
            queryset = queryset.filter(category__slug=category)
        if level:
            queryset = queryset.filter(level=level)
        if is_free == 'true':
            queryset = queryset.filter(is_free=True)
        elif is_free == 'false':
            queryset = queryset.filter(is_free=False)
        queryset = queryset.annotate(student_count=Count('enrollments', distinct=True))
        sort_options = ['-created_at', 'created_at', 'title', '-student_count']
        if sort in sort_options:
            queryset = queryset.order_by(sort)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['search'] = self.request.GET.get('search', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_level'] = self.request.GET.get('level', '')
        context['total_courses'] = Course.objects.published().count()
        return context


class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course_detail.html'
    context_object_name = 'course'
    slug_field = 'slug'

    def get_object(self):
        obj = super().get_object()
        Course.objects.filter(pk=obj.pk).update(views=F('views') + 1)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        user = self.request.user
        notes = course.notes.all()
        context['notes'] = notes
        if user.is_authenticated:
            context['is_enrolled'] = Enrollment.objects.filter(
                student=user, course=course, is_active=True
            ).exists()
        else:
            context['is_enrolled'] = False
        context['enrollment_count'] = course.enrollments.filter(is_active=True).count()
        return context


class CourseCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'

    def test_func(self):
        return self.request.user.is_teacher or self.request.user.is_staff

    def form_valid(self, form):
        form.instance.teacher = self.request.user
        messages.success(self.request, 'Course created successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('courses:detail', kwargs={'slug': self.object.slug})


class CourseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'courses/course_form.html'

    def test_func(self):
        course = self.get_object()
        return self.request.user == course.teacher or self.request.user.is_staff

    def form_valid(self, form):
        messages.success(self.request, 'Course updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('courses:detail', kwargs={'slug': self.object.slug})


class CourseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Course
    template_name = 'courses/course_confirm_delete.html'
    success_url = reverse_lazy('courses:list')

    def test_func(self):
        course = self.get_object()
        return self.request.user == course.teacher or self.request.user.is_staff

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Course deleted successfully.')
        return super().delete(request, *args, **kwargs)


@login_required
def enroll_course(request, slug):
    """
    Enroll student — sends enrollment confirmation email.
    If course is paid → sends invoice email instead.
    """
    course = get_object_or_404(Course, slug=slug, status='published')

    if not request.user.is_student:
        messages.error(request, 'Only students can enroll.')
        return redirect('courses:detail', slug=slug)

    if course.is_full:
        messages.warning(request, 'This course is full.')
        return redirect('courses:detail', slug=slug)

    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course,
        defaults={'is_active': True}
    )

    if created:
        # ── Send emails ────────────────────────────────────────────────
        try:
            from lms_project.email_service import (
                send_enrollment_confirmation_email,
                send_course_invoice_email,
            )
            if course.is_free:
                send_enrollment_confirmation_email(request.user, course, enrollment)
                messages.success(request, f'🎉 Enrolled in "{course.title}"! Check your email for confirmation.')
            else:
                send_course_invoice_email(request.user, course, enrollment)
                messages.success(request, f'✅ Enrolled in "{course.title}"! Invoice sent to {request.user.email}')
        except Exception:
            messages.success(request, f'Enrolled in "{course.title}" successfully!')
    else:
        if enrollment.is_active:
            messages.info(request, 'You are already enrolled.')
        else:
            enrollment.is_active = True
            enrollment.save()
            messages.success(request, 'Re-enrolled successfully!')

    return redirect('courses:detail', slug=slug)


@login_required
def unenroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug)
    if request.method == 'POST':
        Enrollment.objects.filter(student=request.user, course=course).update(is_active=False)
        messages.success(request, f'Unenrolled from "{course.title}".')
    return redirect('courses:detail', slug=slug)


@login_required
def upload_note(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    if request.user != course.teacher and not request.user.is_staff:
        messages.error(request, 'Only the course teacher can upload notes.')
        return redirect('courses:detail', slug=course_slug)
    form = NoteForm()
    if request.method == 'POST':
        form = NoteForm(request.POST, request.FILES)
        if form.is_valid():
            note = form.save(commit=False)
            note.course = course
            note.uploaded_by = request.user
            note.save()
            messages.success(request, 'Note uploaded successfully!')
            return redirect('courses:detail', slug=course_slug)
    return render(request, 'courses/upload_note.html', {'form': form, 'course': course})


@login_required
def download_note(request, note_id):
    note = get_object_or_404(Note, pk=note_id)
    course = note.course
    if request.user.is_student:
        if not Enrollment.objects.filter(
            student=request.user, course=course, is_active=True
        ).exists():
            messages.error(request, 'You must be enrolled to download notes.')
            return redirect('courses:detail', slug=course.slug)
    try:
        return FileResponse(
            note.file.open('rb'),
            as_attachment=True,
            filename=note.file.name.split('/')[-1]
        )
    except Exception:
        raise Http404("File not found.")


@login_required
def teacher_courses(request):
    if not request.user.is_teacher and not request.user.is_staff:
        return redirect('dashboard:index')
    courses = Course.objects.filter(teacher=request.user).annotate(
        student_count=Count('enrollments', distinct=True),
    ).order_by('-created_at')
    return render(request, 'courses/teacher_courses.html', {'courses': courses})


@login_required
def student_courses(request):
    if not request.user.is_student:
        return redirect('dashboard:index')
    enrollments = Enrollment.objects.filter(
        student=request.user, is_active=True
    ).select_related('course', 'course__teacher', 'course__category')
    return render(request, 'courses/student_courses.html', {'enrollments': enrollments})
