from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/dashboard/', permanent=False)),

    path('accounts/', include('accounts.urls', namespace='accounts')),
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
