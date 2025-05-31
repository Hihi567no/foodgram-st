"""
URL configuration for foodgram_backend project.

This module defines the main URL routing for the Foodgram application,
including API endpoints, admin interface, and media file serving.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from api.views import recipe_short_link_redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('s/<int:recipe_id>/', recipe_short_link_redirect,
         name='recipe_short_link'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
