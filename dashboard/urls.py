from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('student/', views.student_dashboard, name='student'),
    path('teacher/', views.teacher_dashboard, name='teacher'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('super-admin/', views.super_admin_dashboard, name='super_admin'),
]
