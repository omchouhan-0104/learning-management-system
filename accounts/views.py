"""
Accounts Views
Topics: FBV, CBV, Authentication, Sessions, Cookies,
        LoginRequiredMixin, UserPassesTestMixin, Email Verification
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.db.models import Q

from .models import User, EmailConfirmationToken
from .forms import RegisterForm, LoginForm, ProfileUpdateForm, CustomPasswordChangeForm, UserAdminForm


def is_admin_or_super(user):
    return user.is_staff or user.is_superuser


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            request.session['user_role'] = user.role
            messages.success(
                request,
                f'Welcome {user.first_name}! Account created. '
                f'A confirmation email has been sent to {user.email}.'
            )
            return redirect(user.get_dashboard_url())
        else:
            messages.error(request, 'Please fix the errors below.')
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            request.session['user_role'] = user.role
            if not request.POST.get('remember_me'):
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(86400 * 30)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            next_url = request.GET.get('next', user.get_dashboard_url())
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Logged out successfully.')
        return redirect('accounts:login')
    return render(request, 'accounts/logout_confirm.html')


@login_required
def profile_view(request):
    form = ProfileUpdateForm(instance=request.user)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated!')
            return redirect('accounts:profile')
    return render(request, 'accounts/profile.html', {'form': form})


@login_required
def change_password_view(request):
    form = CustomPasswordChangeForm(user=request.user)
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('accounts:profile')
    return render(request, 'accounts/change_password.html', {'form': form})


def verify_email_view(request, token):
    """
    Email verification view.
    Marks user as email-verified when they click the link.
    """
    try:
        token_obj = EmailConfirmationToken.objects.get(token=token, is_used=False)
    except EmailConfirmationToken.DoesNotExist:
        messages.error(request, 'Invalid or expired verification link.')
        return redirect('accounts:login')

    if token_obj.is_expired:
        messages.error(request, 'This verification link has expired. Please request a new one.')
        return redirect('accounts:resend_verification')

    user = token_obj.user
    user.is_email_verified = True
    user.save()
    token_obj.is_used = True
    token_obj.save()

    messages.success(request, '✅ Email verified successfully! You can now use all features.')
    if not request.user.is_authenticated:
        login(request, user)
    return redirect(user.get_dashboard_url())


@login_required
def resend_verification_email(request):
    """Resend email verification link."""
    user = request.user
    if user.is_email_verified:
        messages.info(request, 'Your email is already verified.')
        return redirect('dashboard:index')

    if request.method == 'POST':
        from lms_project.email_service import send_confirm_email
        token_obj, _ = EmailConfirmationToken.objects.get_or_create(user=user)
        # Reset token
        import uuid
        token_obj.token = uuid.uuid4()
        token_obj.is_used = False
        token_obj.save()
        send_confirm_email(user, str(token_obj.token))
        messages.success(request, f'Verification email resent to {user.email}')
        return redirect('dashboard:index')

    return render(request, 'accounts/resend_verification.html')


class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by = 10

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def get_queryset(self):
        queryset = User.objects.all()
        search = self.request.GET.get('search', '')
        role_filter = self.request.GET.get('role', '')
        status_filter = self.request.GET.get('status', '')
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        if role_filter:
            queryset = queryset.filter(role=role_filter)
        if status_filter == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_filter == 'inactive':
            queryset = queryset.filter(is_active=False)
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_students'] = User.objects.filter(role='student').count()
        context['total_teachers'] = User.objects.filter(role='teacher').count()
        context['search'] = self.request.GET.get('search', '')
        context['role_filter'] = self.request.GET.get('role', '')
        return context


class UserDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = User
    template_name = 'accounts/user_detail.html'
    context_object_name = 'profile_user'

    def test_func(self):
        return self.request.user.is_staff or self.request.user.pk == self.kwargs['pk']


class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = UserAdminForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, 'User updated successfully!')
        return super().form_valid(form)


@login_required
@user_passes_test(is_admin_or_super)
def toggle_user_status(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, "You cannot deactivate your own account.")
        return redirect('accounts:user_list')
    user.is_active = not user.is_active
    user.save()
    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'User {user.username} {status}.')
    return redirect('accounts:user_list')
