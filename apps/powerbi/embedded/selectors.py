from django.db.models import Q

from apps.core.common.access import can_view_reports, get_accessible_properties, user_is_admin
from apps.powerbi.embedded.models import PowerBIReport, ReportGroup


def get_accessible_report_groups(user):
    if not getattr(user, 'is_authenticated', False) or not can_view_reports(user):
        return ReportGroup.objects.none()
    queryset = ReportGroup.objects.filter(is_active=True).prefetch_related('reports').order_by('sort_order', 'name')
    if user_is_admin(user):
        return queryset
    properties = get_accessible_properties(user)
    return queryset.filter(property_subscriptions__property__in=properties, property_subscriptions__is_active=True).distinct()


def get_accessible_reports(user, group=None):
    if not getattr(user, 'is_authenticated', False) or not can_view_reports(user):
        return PowerBIReport.objects.none()
    queryset = PowerBIReport.objects.filter(is_active=True, report_group__is_active=True).select_related('report_group').order_by('report_group__sort_order', 'sort_order', 'name')
    if group is not None:
        queryset = queryset.filter(report_group=group)
    if not user_is_admin(user):
        queryset = queryset.filter(report_group__property_subscriptions__property__in=get_accessible_properties(user), report_group__property_subscriptions__is_active=True).distinct()
        allowed = []
        for report in queryset:
            if not report.allowed_role_list or user.groups.filter(name__in=report.allowed_role_list).exists():
                allowed.append(report.pk)
        queryset = queryset.filter(pk__in=allowed)
    return queryset


def user_can_view_report(user, report):
    return get_accessible_reports(user).filter(pk=report.pk).exists()
