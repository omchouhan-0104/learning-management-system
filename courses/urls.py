from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.CourseListView.as_view(), name='list'),
    path('create/', views.CourseCreateView.as_view(), name='create'),
    path('my-courses/', views.teacher_courses, name='teacher_courses'),
    path('enrolled/', views.student_courses, name='student_courses'),
    path('<slug:slug>/', views.CourseDetailView.as_view(), name='detail'),
    path('<slug:slug>/edit/', views.CourseUpdateView.as_view(), name='edit'),
    path('<slug:slug>/delete/', views.CourseDeleteView.as_view(), name='delete'),
    path('<slug:slug>/enroll/', views.enroll_course, name='enroll'),
    path('<slug:slug>/unenroll/', views.unenroll_course, name='unenroll'),
    path('<slug:course_slug>/notes/upload/', views.upload_note, name='upload_note'),
    path('notes/<int:note_id>/download/', views.download_note, name='download_note'),
]
