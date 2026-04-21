from django.conf import settings
from django.utils import timezone

from apps.core.common.access import (
    actor_highest_role,
    can_manage_mappings,
    can_manage_users,
    can_view_dataops,
    can_view_mappings,
    can_view_reports,
    get_accessible_properties,
    get_current_property,
)


def global_ui(request):
    context = {
        # 'APP_NAME': settings.APP_NAME,
        # 'APP_SLOGAN': settings.APP_NAME,
        # 'APP_LOGO': settings.APP_NAME,
        "APP_NAME": getattr(settings, "APP_NAME", "ROInsight"),
        "APP_SLOGAN": getattr(settings, "APP_SLOGAN", ""),
        "APP_LOGO": getattr(settings, "APP_LOGO", "img/logo.png"),
        'TAILWIND_USE_CDN': settings.TAILWIND_USE_CDN,
        'available_properties': [],
        'current_property': None,
        'latest_notifications': [],
        'unread_notifications_count': 0,
        'active_announcements_count': 0,
        'accessible_report_groups': [],
        'highest_role': '',
        'theme_preference': 'system',
        'can_manage_users': False,
        'can_manage_mappings': False,
        'can_view_mappings': False,
        'can_view_reports': False,
        'can_view_dataops': False,
    }
    if not getattr(request, 'user', None) or not request.user.is_authenticated:
        return context

    available_properties = get_accessible_properties(request.user)
    current_property = get_current_property(request, request.user, available_properties)

    from apps.notifications.inbox.models import Notification
    from apps.notifications.announcements.models import Announcement
    from apps.powerbi.embedded.selectors import get_accessible_report_groups

    latest_notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:5]
    active_announcements = Announcement.objects.filter(is_published=True).filter_active(now=timezone.now())
    accessible_announcements = [announcement for announcement in active_announcements if announcement.is_visible_to_user(request.user)]
    profile = getattr(request.user, 'profile', None)

    context.update(
        {
            'available_properties': available_properties,
            'current_property': current_property,
            'latest_notifications': latest_notifications,
            'unread_notifications_count': Notification.objects.filter(recipient=request.user, read_at__isnull=True).count(),
            'active_announcements_count': len(accessible_announcements),
            'accessible_report_groups': get_accessible_report_groups(request.user)[:6],
            'highest_role': actor_highest_role(request.user),
            'theme_preference': getattr(profile, 'theme_preference', 'system') if profile else 'system',
            'can_manage_users': can_manage_users(request.user),
            'can_manage_mappings': can_manage_mappings(request.user),
            'can_view_mappings': can_view_mappings(request.user),
            'can_view_reports': can_view_reports(request.user),
            'can_view_dataops': can_view_dataops(request.user),
        }
    )
    return context



# def sidebar_navigation(request):
#     if not request.user.is_authenticated:
#         return {"sidebar_menu": []}

#     return {
#         "sidebar_menu": build_sidebar_menu(request),
#     }


from apps.core.common.header_navigation import build_header_menu
from apps.core.common.sidebar_navigation import build_sidebar_menu


def app_navigation(request):
    if not request.user.is_authenticated:
        return {
            "sidebar_menu": [],
            "header_menu": [],
        }

    return {
        "sidebar_menu": build_sidebar_menu(request),
        "header_menu": build_header_menu(request),
    }