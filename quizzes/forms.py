from django import forms
from django.forms import inlineformset_factory
from .models import Quiz, Question, Option


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'time_limit_minutes', 'passing_score', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Quiz title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Optional description'}),
            'time_limit_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'passing_score': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 100}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'marks', 'order']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Enter your question here...'}),
            'question_type': forms.Select(attrs={'class': 'form-control'}),
            'marks': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }


class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['text', 'is_correct']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Option text'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# Inline formset: 4 options per question
OptionFormSet = inlineformset_factory(
    Question, Option,
    form=OptionForm,
    fields=['text', 'is_correct'],
    extra=4,
    max_num=6,
    can_delete=True,
)
