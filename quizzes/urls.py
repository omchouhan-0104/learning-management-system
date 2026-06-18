from django.urls import path
from . import views

app_name = 'quizzes'

urlpatterns = [
    path('course/<slug:course_slug>/create/', views.QuizCreateView.as_view(), name='create'),
    path('<int:pk>/edit/', views.QuizUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.QuizDeleteView.as_view(), name='delete'),
    path('<int:pk>/questions/', views.manage_questions, name='manage_questions'),
    path('<int:quiz_pk>/questions/add/', views.add_question, name='add_question'),
    path('question/<int:question_pk>/edit/', views.edit_question, name='edit_question'),
    path('question/<int:question_pk>/delete/', views.delete_question, name='delete_question'),
    path('<int:pk>/', views.quiz_detail, name='detail'),
    path('<int:pk>/take/', views.take_quiz, name='take'),
    path('<int:pk>/result/', views.quiz_result, name='result'),
]
