from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'full_name', 'email', 'role_badge', 'is_active_icon', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']
    list_per_page = 20

    fieldsets = (
        ('Account Info', {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'bio', 'phone', 'date_of_birth', 'profile_image')}),
        ('Role & Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Timestamps', {'fields': ('created_at', 'last_login'), 'classes': ('collapse',)}),
    )
    readonly_fields = ['created_at', 'last_login']

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'role', 'password1', 'password2'),
        }),
    )

    def full_name(self, obj):
        return obj.get_full_name() or '—'
    full_name.short_description = 'Name'

    def role_badge(self, obj):
        colors = {'super_admin': '#dc3545', 'admin': '#fd7e14', 'teacher': '#0d6efd', 'student': '#198754'}
        color = colors.get(obj.role, '#6c757d')
        return format_html('<span style="background:{};color:white;padding:2px 8px;border-radius:10px;font-size:11px">{}</span>', color, obj.get_role_display())
    role_badge.short_description = 'Role'

    def is_active_icon(self, obj):
        return '✅' if obj.is_active else '❌'
    is_active_icon.short_description = 'Active'

    actions = ['activate_users', 'deactivate_users', 'make_teacher', 'make_student']

    def activate_users(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} user(s) activated.')
    activate_users.short_description = 'Activate selected users'

    def deactivate_users(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} user(s) deactivated.')
    deactivate_users.short_description = 'Deactivate selected users'

    def make_teacher(self, request, queryset):
        queryset.update(role='teacher')
        self.message_user(request, 'Users set as Teacher.')
    make_teacher.short_description = 'Set role: Teacher'

    def make_student(self, request, queryset):
        queryset.update(role='student')
        self.message_user(request, 'Users set as Student.')
    make_student.short_description = 'Set role: Student'
