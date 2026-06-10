"""
Quizzes Views — fully working quiz CRUD + question management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.db.models import Avg, Count, Max, Min
from django.http import JsonResponse

from courses.models import Course, Enrollment
from .models import Quiz, Question, Option, QuizAttempt, StudentAnswer
from .forms import QuizForm, QuestionForm, OptionFormSet


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _is_teacher_of_quiz(user, quiz):
    return user == quiz.course.teacher or user.is_staff


# ─── Quiz CRUD ────────────────────────────────────────────────────────────────

class QuizCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Quiz
    form_class = QuizForm
    template_name = 'quizzes/quiz_form.html'

    def test_func(self):
        course = get_object_or_404(Course, slug=self.kwargs['course_slug'])
        return self.request.user == course.teacher or self.request.user.is_staff

    def form_valid(self, form):
        course = get_object_or_404(Course, slug=self.kwargs['course_slug'])
        form.instance.course = course
        response = super().form_valid(form)
        messages.success(self.request, f'Quiz "{self.object.title}" created! Now add questions below.')
        return response

    def get_success_url(self):
        # After creating, go straight to question management
        return reverse('quizzes:manage_questions', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = get_object_or_404(Course, slug=self.kwargs['course_slug'])
        context['page_title'] = 'Create Quiz'
        return context


class QuizUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Quiz
    form_class = QuizForm
    template_name = 'quizzes/quiz_form.html'

    def test_func(self):
        return _is_teacher_of_quiz(self.request.user, self.get_object())

    def form_valid(self, form):
        messages.success(self.request, 'Quiz updated!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('quizzes:detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.object.course
        context['page_title'] = 'Edit Quiz'
        return context


class QuizDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Quiz
    template_name = 'quizzes/quiz_confirm_delete.html'

    def test_func(self):
        return _is_teacher_of_quiz(self.request.user, self.get_object())

    def get_success_url(self):
        return reverse('courses:detail', kwargs={'slug': self.object.course.slug})

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Quiz deleted.')
        return super().delete(request, *args, **kwargs)


# ─── Question Management ──────────────────────────────────────────────────────

@login_required
def manage_questions(request, pk):
    """
    The main question builder page.
    Shows all existing questions + an 'Add Question' button.
    Teachers use this to build out the entire quiz.
    """
    quiz = get_object_or_404(Quiz, pk=pk)
    if not _is_teacher_of_quiz(request.user, quiz):
        messages.error(request, 'Permission denied.')
        return redirect('quizzes:detail', pk=pk)

    questions = quiz.questions.prefetch_related('options').order_by('order')
    return render(request, 'quizzes/manage_questions.html', {
        'quiz': quiz,
        'questions': questions,
        'question_count': questions.count(),
    })


@login_required
def add_question(request, quiz_pk):
    """
    Add a new question with its options (using inline formset).
    Renders a form with the question fields + 4 option rows.
    """
    quiz = get_object_or_404(Quiz, pk=quiz_pk)
    if not _is_teacher_of_quiz(request.user, quiz):
        messages.error(request, 'Permission denied.')
        return redirect('quizzes:detail', pk=quiz_pk)

    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.quiz = quiz
            # Auto-set order if not provided
            if not question.order:
                last = quiz.questions.order_by('-order').first()
                question.order = (last.order + 1) if last else 1
            question.save()

            option_formset = OptionFormSet(request.POST, instance=question)
            if option_formset.is_valid():
                options = option_formset.save(commit=False)
                saved_count = 0
                for opt in options:
                    if opt.text.strip():  # only save non-empty options
                        opt.question = question
                        opt.save()
                        saved_count += 1
                # Delete marked-for-deletion options
                for opt in option_formset.deleted_objects:
                    opt.delete()

                if saved_count == 0:
                    question.delete()
                    messages.error(request, 'Please add at least one option.')
                    return redirect('quizzes:add_question', quiz_pk=quiz_pk)

                # Validate: at least one correct answer
                if not question.options.filter(is_correct=True).exists():
                    messages.warning(request, f'Question saved but has no correct answer marked. Edit it to fix.')
                else:
                    messages.success(request, f'Question {question.order} added successfully!')

                return redirect('quizzes:manage_questions', pk=quiz_pk)
            else:
                question.delete()  # rollback question if options invalid
                messages.error(request, 'Please fix option errors.')
        else:
            option_formset = OptionFormSet(request.POST)
    else:
        # Pre-fill order
        last = quiz.questions.order_by('-order').first()
        next_order = (last.order + 1) if last else 1
        question_form = QuestionForm(initial={'order': next_order, 'marks': 1})
        option_formset = OptionFormSet()

    return render(request, 'quizzes/add_question.html', {
        'quiz': quiz,
        'question_form': question_form,
        'option_formset': option_formset,
    })


@login_required
def edit_question(request, question_pk):
    """Edit an existing question and its options."""
    question = get_object_or_404(Question, pk=question_pk)
    quiz = question.quiz
    if not _is_teacher_of_quiz(request.user, quiz):
        messages.error(request, 'Permission denied.')
        return redirect('quizzes:detail', pk=quiz.pk)

    if request.method == 'POST':
        question_form = QuestionForm(request.POST, instance=question)
        option_formset = OptionFormSet(request.POST, instance=question)
        if question_form.is_valid() and option_formset.is_valid():
            question_form.save()
            options = option_formset.save(commit=False)
            for opt in options:
                if opt.text.strip():
                    opt.question = question
                    opt.save()
            for opt in option_formset.deleted_objects:
                opt.delete()
            messages.success(request, 'Question updated!')
            return redirect('quizzes:manage_questions', pk=quiz.pk)
    else:
        question_form = QuestionForm(instance=question)
        option_formset = OptionFormSet(instance=question)

    return render(request, 'quizzes/edit_question.html', {
        'quiz': quiz,
        'question': question,
        'question_form': question_form,
        'option_formset': option_formset,
    })


@login_required
def delete_question(request, question_pk):
    """Delete a question and all its options."""
    question = get_object_or_404(Question, pk=question_pk)
    quiz = question.quiz
    if not _is_teacher_of_quiz(request.user, quiz):
        messages.error(request, 'Permission denied.')
        return redirect('quizzes:detail', pk=quiz.pk)
    if request.method == 'POST':
        question.delete()
        messages.success(request, 'Question deleted.')
    return redirect('quizzes:manage_questions', pk=quiz.pk)


# ─── Quiz Detail (teacher + student view) ────────────────────────────────────

@login_required
def quiz_detail(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    questions = quiz.questions.prefetch_related('options').order_by('order')
    has_attempted = False
    user_attempt = None
    stats = None

    if request.user.is_student:
        has_attempted = QuizAttempt.objects.filter(student=request.user, quiz=quiz).exists()
        user_attempt = QuizAttempt.objects.filter(student=request.user, quiz=quiz).first()

    if _is_teacher_of_quiz(request.user, quiz):
        stats = quiz.attempts.aggregate(
            avg_score=Avg('percentage'),
            total_attempts=Count('id'),
            max_score=Max('percentage'),
            min_score=Min('percentage'),
        )

    return render(request, 'quizzes/quiz_detail.html', {
        'quiz': quiz,
        'questions': questions,
        'has_attempted': has_attempted,
        'user_attempt': user_attempt,
        'stats': stats,
        'is_teacher': _is_teacher_of_quiz(request.user, quiz),
    })


# ─── Take Quiz ────────────────────────────────────────────────────────────────

@login_required
def take_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk, is_active=True)

    if not request.user.is_student:
        messages.error(request, 'Only students can take quizzes.')
        return redirect('quizzes:detail', pk=pk)

    if not Enrollment.objects.filter(
        student=request.user, course=quiz.course, is_active=True
    ).exists():
        messages.error(request, 'You must be enrolled in this course to take this quiz.')
        return redirect('courses:detail', slug=quiz.course.slug)

    if QuizAttempt.objects.filter(student=request.user, quiz=quiz).exists():
        messages.warning(request, 'You have already attempted this quiz.')
        return redirect('quizzes:result', pk=pk)

    questions = list(quiz.questions.prefetch_related('options').order_by('order'))

    if not questions:
        messages.error(request, 'This quiz has no questions yet. Please check back later.')
        return redirect('quizzes:detail', pk=pk)

    if request.method == 'POST':
        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            student=request.user,
            submitted_at=timezone.now(),
            total_marks=sum(q.marks for q in questions)
        )
        score = 0
        for question in questions:
            option_id = request.POST.get(f'question_{question.pk}')
            is_correct = False
            selected_option = None
            if option_id:
                try:
                    selected_option = Option.objects.get(pk=int(option_id), question=question)
                    is_correct = selected_option.is_correct
                    if is_correct:
                        score += question.marks
                except Option.DoesNotExist:
                    pass
            StudentAnswer.objects.create(
                attempt=attempt,
                question=question,
                selected_option=selected_option,
                is_correct=is_correct
            )

        total = attempt.total_marks or 1
        percentage = round((score / total) * 100, 2)
        attempt.score = score
        attempt.percentage = percentage
        attempt.passed = percentage >= quiz.passing_score
        attempt.save()
        messages.success(request, f'Quiz submitted! You scored {percentage}%')
        return redirect('quizzes:result', pk=pk)

    return render(request, 'quizzes/take_quiz.html', {
        'quiz': quiz,
        'questions': questions,
    })


# ─── Quiz Result ──────────────────────────────────────────────────────────────

@login_required
def quiz_result(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    attempt = QuizAttempt.objects.filter(student=request.user, quiz=quiz).first()
    if not attempt:
        messages.error(request, 'No attempt found.')
        return redirect('quizzes:detail', pk=pk)
    answers = attempt.answers.select_related(
        'question', 'selected_option'
    ).prefetch_related('question__options').order_by('question__order')
    return render(request, 'quizzes/result.html', {
        'quiz': quiz,
        'attempt': attempt,
        'answers': answers,
    })
