from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import set_language

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('set-language/', set_language, name='set_language'),
]

# Serve media files in development and on Render
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
