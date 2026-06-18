from django import forms
from .models import Assignment, AssignmentSubmission

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'due_date', 'total_marks', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'due_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['file', 'remarks']
        widgets = {
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional remarks'}),
        }

class GradeForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['marks_obtained', 'teacher_feedback']
        widgets = {
            'marks_obtained': forms.NumberInput(attrs={'class': 'form-control'}),
            'teacher_feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
