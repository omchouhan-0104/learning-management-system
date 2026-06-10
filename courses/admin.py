from django.contrib import admin
from django.utils.html import format_html
from .models import Course, Category, Enrollment, Note


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'category', 'status_badge', 'level', 'enrollment_count', 'created_at']
    list_filter = ['status', 'level', 'category', 'is_free', 'created_at']
    search_fields = ['title', 'description', 'teacher__username']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views', 'created_at', 'updated_at']
    list_per_page = 20

    def status_badge(self, obj):
        colors = {'published': '#198754', 'draft': '#6c757d', 'archived': '#dc3545'}
        color = colors.get(obj.status, '#6c757d')
        return format_html('<span style="color:{};font-weight:bold">{}</span>', color, obj.status.upper())
    status_badge.short_description = 'Status'

    def enrollment_count(self, obj):
        return obj.enrollments.filter(is_active=True).count()
    enrollment_count.short_description = 'Students'

    actions = ['publish_courses', 'archive_courses']

    def publish_courses(self, request, queryset):
        queryset.update(status='published')
        self.message_user(request, 'Courses published.')
    publish_courses.short_description = 'Publish selected courses'

    def archive_courses(self, request, queryset):
        queryset.update(status='archived')
        self.message_user(request, 'Courses archived.')
    archive_courses.short_description = 'Archive selected courses'


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrolled_at', 'is_active', 'progress']
    list_filter = ['is_active', 'completed', 'enrolled_at']
    search_fields = ['student__username', 'course__title']


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'uploaded_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['title', 'course__title']
