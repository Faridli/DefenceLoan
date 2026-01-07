from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static 
from django.contrib.auth import views as auth_views
from core.views import home
urlpatterns = [
    path('admin/', admin.site.urls),

    # Auth URLs
    path('sign-in/', auth_views.LoginView.as_view(template_name='users/sign_in.html'), name='sign-in'),
    
    # App URLs 
    path('',home,name='home'),
    path('tasks/', include('tasks.urls')),
    path('users/', include('users.urls')), 
    
]

# Debug Toolbar only in DEBUG mode
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
