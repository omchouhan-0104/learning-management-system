from django.urls import path
from . import views

app_name = 'assignments'

urlpatterns = [
    path('course/<slug:course_slug>/create/', views.AssignmentCreateView.as_view(), name='create'),
    path('<int:assignment_id>/submit/', views.submit_assignment, name='submit'),
    path('<int:assignment_id>/submissions/', views.assignment_submissions, name='submissions'),
    path('submission/<int:submission_id>/grade/', views.grade_submission, name='grade'),
]
