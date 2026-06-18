"""
Root URL Configuration
Topic: URL Routing, include(), path(), re_path()
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),

    # Our custom accounts app (login, logout, register, profile, etc.)
    path('accounts/', include('accounts.urls', namespace='accounts')),

    # Django built-in auth ONLY for password reset URLs
    # These are: password_reset/, password_reset/done/, reset/<uidb64>/<token>/, reset/done/
    # We exclude login/ and logout/ since our accounts app handles those
    path('accounts/password_reset/', include('django.contrib.auth.urls')),

    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('courses/', include('courses.urls', namespace='courses')),
    path('assignments/', include('assignments.urls', namespace='assignments')),
    path('quizzes/', include('quizzes.urls', namespace='quizzes')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = 'EduLearn LMS Administration'
admin.site.site_title = 'LMS Admin Portal'
admin.site.index_title = 'Welcome to LMS Admin'
