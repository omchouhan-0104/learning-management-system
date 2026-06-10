from django.contrib import admin
from .models import Assignment, AssignmentSubmission

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'due_date', 'total_marks', 'submission_count']
    list_filter = ['due_date', 'course']
    search_fields = ['title', 'course__title']

    def submission_count(self, obj):
        return obj.submissions.count()
    submission_count.short_description = 'Submissions'

@admin.register(AssignmentSubmission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'assignment', 'submitted_at', 'is_graded', 'marks_obtained']
    list_filter = ['is_graded', 'submitted_at']
    search_fields = ['student__username', 'assignment__title']
