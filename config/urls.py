from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

def superuser_only_has_permission(request):
    user = request.user
    return bool(
        user.is_authenticated and
        user.is_active and
        user.is_superuser
    )


admin.site.has_permission = superuser_only_has_permission
admin.site.site_header = 'ROInsight Administration'
admin.site.site_title = 'ROInsight Admin'
admin.site.index_title = 'Platform administration'


def root_redirect(request):
    return redirect('dashboard:home')


urlpatterns = [
    path('', root_redirect, name='root'),
    path('admin/', admin.site.urls),
    # path('admin/', admin_site.urls),
    path('accounts/', include('apps.usermanagement.users.auth_urls')),
    path('dashboard/', include(('apps.dashboard.home.urls', 'dashboardhome'), namespace='dashboard')),
    path('users/', include(('apps.usermanagement.users.urls', 'usercore'), namespace='users')),
    path('profile/', include(('apps.usermanagement.profiles.urls', 'profilecore'), namespace='profiles')),
    path('properties/', include(('apps.properties.core.urls', 'propertycore'), namespace='properties')),
    path('notifications/', include(('apps.notifications.inbox.urls', 'notificationsinbox'), namespace='notifications')),
    path('announcements/', include(('apps.notifications.announcements.urls', 'notificationsannouncements'), namespace='announcements')),
    path('analytics/', include(('apps.analytics.kpi.urls', 'analyticskpi'), namespace='analytics')),
    path('reports/', include(('apps.powerbi.embedded.urls', 'powerbiembedded'), namespace='powerbi')),
    path('dataops/', include(('apps.dataops.files.urls', 'dataopsfiles'), namespace='dataops')),
    path('settings/mappings/', include(('apps.settings.mappings.urls', 'settingsmappings'), namespace='settings_mappings')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
    path("__reload__/", include("django_browser_reload.urls")),
]