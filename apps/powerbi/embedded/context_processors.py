# apps/powerbi/embedded/context_processors.py
from apps.powerbi.embedded.selectors import get_accessible_report_groups, get_accessible_reports

DEFAULT_GROUP_ICON = "fa-folder"
DEFAULT_GROUP_COLOR = "sky"
DEFAULT_REPORT_ICON = "fa-file-alt"


def report_menu(request):
    user = getattr(request, "user", None)

    if not user or not user.is_authenticated:
        return {
            "report_menu": [],
            "can_view_reports_menu": False,
        }

    groups = get_accessible_report_groups(user)
    reports = get_accessible_reports(user).select_related("report_group")

    reports_by_group = {}
    for report in reports:
        reports_by_group.setdefault(report.report_group_id, []).append(report)

    menu = []
    for group in groups:
        group_reports = reports_by_group.get(group.id, [])
        if not group_reports:
            continue

        menu.append(
            {
                "title": group.name,
                "slug": group.slug,
                "icon": group.icon or DEFAULT_GROUP_ICON,
                "color": (group.color or DEFAULT_GROUP_COLOR).strip(),
                "url": group.get_absolute_url(),
                "items": [
                    {
                        "title": report.name,
                        "slug": report.slug,
                        "icon": DEFAULT_REPORT_ICON,
                        "url": report.get_absolute_url(),
                    }
                    for report in group_reports
                ],
            }
        )

    return {
        "report_menu": menu,
        "can_view_reports_menu": bool(menu),
    }