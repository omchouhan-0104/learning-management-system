from django import forms
from .models import Course, Note, Category

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'description', 'category', 'thumbnail', 'status',
                  'level', 'duration_weeks', 'max_students', 'is_free', 'price']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Course Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'level': forms.Select(attrs={'class': 'form-control'}),
            'duration_weeks': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'max_students': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        is_free = cleaned_data.get('is_free')
        price = cleaned_data.get('price')
        if not is_free and (price is None or price <= 0):
            raise forms.ValidationError('Paid courses must have a price greater than 0.')
        return cleaned_data


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'description', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            allowed = ['.pdf', '.doc', '.docx', '.ppt', '.pptx', '.txt', '.zip']
            ext = '.' + file.name.split('.')[-1].lower()
            if ext not in allowed:
                raise forms.ValidationError(f'Only {", ".join(allowed)} files allowed.')
            if file.size > 10 * 1024 * 1024:  # 10MB
                raise forms.ValidationError('File size must be under 10MB.')
        return file


class CourseSearchForm(forms.Form):
    search = forms.CharField(required=False, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Search courses...'}
    ))
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label='All Categories',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    level = forms.ChoiceField(
        choices=[('', 'All Levels')] + Course.LEVEL_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    is_free = forms.ChoiceField(
        choices=[('', 'All'), ('true', 'Free'), ('false', 'Paid')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
