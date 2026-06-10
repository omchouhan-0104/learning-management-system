"""
Accounts Forms
Topics: Forms, ModelForms, Widgets, Validation, clean_email(), clean(), multi-field validation
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from .models import User


class RegisterForm(UserCreationForm):
    """
    Registration Form
    Topics: ModelForms, Widgets, Validation, clean_email(), password matching
    """
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email Address'
        })
    )
    role = forms.ChoiceField(
        choices=[('student', 'Student'), ('teacher', 'Teacher')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
        }

    # ── Field-Level Validation ──────────────────────────────────────────────
    def clean_email(self):
        """Topic: clean_email() - field level validation"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email is already registered.')
        if len(email) > 254:
            raise ValidationError('Email address is too long.')
        return email.lower()

    def clean_username(self):
        """Topic: Field-level validation"""
        username = self.cleaned_data.get('username')
        if len(username) < 3:
            raise ValidationError('Username must be at least 3 characters.')
        if not username.isalnum():
            raise ValidationError('Username can only contain letters and numbers.')
        return username.lower()

    # ── Multi-field Validation ──────────────────────────────────────────────
    def clean(self):
        """Topic: clean() - multi-field / cross-field validation"""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        first_name = cleaned_data.get('first_name', '')
        last_name = cleaned_data.get('last_name', '')
        email = cleaned_data.get('email', '')

        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords do not match.')

        # Prevent email containing name (multi-field check)
        if email and (first_name.lower() in email.lower() or last_name.lower() in email.lower()):
            pass  # Just an example of multi-field logic; not an error here

        return cleaned_data


class LoginForm(AuthenticationForm):
    """
    Login Form with custom styling
    Topic: Authentication, Widgets
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


class ProfileUpdateForm(forms.ModelForm):
    """
    Profile Update Form
    Topics: ModelForms, ImageField, Widgets
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'bio', 'phone', 'date_of_birth', 'profile_image']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        """Prevent duplicate emails when updating profile"""
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('This email is already in use by another account.')
        return email.lower()

    def clean_profile_image(self):
        """Topic: File validation - validate image size"""
        image = self.cleaned_data.get('profile_image')
        if image:
            if hasattr(image, 'size') and image.size > 2 * 1024 * 1024:  # 2MB
                raise ValidationError('Image file too large (max 2MB).')
        return image


class CustomPasswordChangeForm(PasswordChangeForm):
    """
    Password Change Form with custom widgets
    Topic: Password Hashing, Auth System
    """
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Current Password'})
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'New Password'})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm New Password'})
    )


class UserAdminForm(forms.ModelForm):
    """Form for Admin/SuperAdmin to create/edit users"""
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'is_active', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }
