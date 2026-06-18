from django.contrib import admin
from .models import Quiz, Question, Option, QuizAttempt, StudentAnswer

class OptionInline(admin.TabularInline):
    model = Option
    extra = 4

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 2

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'question_count', 'passing_score', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'course__title']
    inlines = [QuestionInline]

    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = 'Questions'

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'quiz', 'question_type', 'marks']
    inlines = [OptionInline]

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['student', 'quiz', 'score', 'percentage', 'passed', 'started_at']
    list_filter = ['passed', 'started_at']
    search_fields = ['student__username', 'quiz__title']
