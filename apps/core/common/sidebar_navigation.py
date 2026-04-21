from __future__ import annotations

from typing import Callable, Optional

from django.urls import NoReverseMatch, reverse

from apps.core.common.access import can_manage_users, can_view_dataops, can_view_mappings, can_view_reports


def safe_reverse(url_name: str, **kwargs) -> str:
    try:
        return reverse(url_name, kwargs=kwargs)
    except NoReverseMatch:
        return "#"


def is_visible(check: Optional[Callable[[object], bool]], user) -> bool:
    if check is None:
        return True
    return check(user)


SIDEBAR_MENU = [
    {
        "title": "Main",
        "items": [
            {
                "label": "Overview",
                "icon": "fas fa-chart-line",
                "url_name": "dashboard:home",
                "active_names": [("dashboard", "home")],
                "icon_classes": "bg-sky-100 text-sky-700 dark:bg-sky-500/10 dark:text-sky-400",
            },
            {
                "label": "Report Groups",
                "icon": "fas fa-file-alt",
                "url_name": "powerbi:group-list",
                "active_names": [
                    ("powerbi", "group-list"),
                    ("powerbi", "group-detail"),
                ],
                "icon_classes": "bg-violet-100 text-violet-700 dark:bg-violet-500/10 dark:text-violet-400",
            },
            # {
            #     "label": "Metrics",
            #     "icon": "fas fa-chart-pie",
            #     "url_name": "analytics:metrics",
            #     "active_names": [("analytics", "metrics")],
            #     "icon_classes": "bg-violet-100 text-violet-700 dark:bg-violet-500/10 dark:text-violet-400",
            # },
            
        ],
    },
    # {
    #     "title": "Reports",
    #     "visible_if": can_view_reports,
    #     "items": [
    #         {
    #             "label": "Report Groups",
    #             "icon": "fas fa-file-alt",
    #             "url_name": "powerbi:group-list",
    #             "active_names": [
    #                 ("powerbi", "group-list"),
    #                 ("powerbi", "group-detail"),
    #             ],
    #             "icon_classes": "bg-violet-100 text-violet-700 dark:bg-violet-500/10 dark:text-violet-400",
    #         },
    #     ],
    # },
    {
        "title": "Analytics",
        "items": [
            {
                "label": "Dashboard",
                "icon": "fas fa-chart-bar",
                "url_name": "analytics:metrics",
                "active_names": [("analytics", "metrics")],
                "icon_classes": "bg-indigo-100 text-indigo-700 dark:bg-indigo-500/10 dark:text-indigo-400",
            },
            {
                "label": "Executive Overview",
                "icon": "fas fa-chart-bar",
                "url_name": "analytics:executive",
                "active_names": [("analytics", "executive")],
                "icon_classes": "bg-indigo-100 text-indigo-700 dark:bg-indigo-500/10 dark:text-indigo-400",
            },
            {
                "label": "Daily Occupancy",
                "icon": "fas fa-bed",
                "url_name": "analytics:occupancy",
                "active_names": [("analytics", "occupancy")],
                "icon_classes": "bg-cyan-100 text-cyan-700 dark:bg-cyan-500/10 dark:text-cyan-400",
            },
            {
                "label": "Total Revenue",
                "icon": "fas fa-coins",
                "url_name": "analytics:revenue",
                "active_names": [("analytics", "revenue")],
                "icon_classes": "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400",
            },
            {
                "label": "Performance",
                "icon": "fas fa-building",
                "url_name": "analytics:properties",
                "active_names": [("analytics", "properties")],
                "icon_classes": "bg-amber-100 text-amber-700 dark:bg-amber-500/10 dark:text-amber-400",
            },
            {
                "label": "Goals & Scorecard",
                "icon": "fas fa-bullseye",
                "url_name": "analytics:goals",
                "active_names": [("analytics", "goals")],
                "icon_classes": "bg-rose-100 text-rose-700 dark:bg-rose-500/10 dark:text-rose-400",
            },
        ],
        "card": True,
    },
    {
        "title": "DataOps",
        "visible_if": can_view_dataops,
        "items": [
            {
                "label": "Operations Dashboard",
                "icon": "fas fa-gears",
                "url_name": "dataops:dashboard",
                "active_names": [("dataops", "dashboard")],
                "icon_classes": "bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300",
            },
            {
                "label": "All Files",
                "icon": "fas fa-folder-open",
                "url_name": "dataops:file-list",
                "active_names": [("dataops", "file-list")],
                "icon_classes": "bg-blue-100 text-blue-700 dark:bg-blue-500/10 dark:text-blue-400",
            },
            {
                "label": "Missing Files",
                "icon": "fas fa-triangle-exclamation",
                "url_name": "dataops:missing-files",
                "active_names": [("dataops", "missing-files")],
                "icon_classes": "bg-red-100 text-red-700 dark:bg-red-500/10 dark:text-red-400",
            },
        ],
        "card": True,
    },
    # {
    #     "title": "Administration",
    #     "items": [
    #         {
    #             "label": "User Management",
    #             "icon": "fas fa-users-cog",
    #             "url_name": "users:list",
    #             "active_names": [("users", "list")],
    #             "visible_if": can_manage_users,
    #             "icon_classes": "bg-amber-100 text-amber-700 dark:bg-amber-500/10 dark:text-amber-400",
    #         },
    #     ],
    # },
    # {
    #     "title": "Settings",
    #     "visible_if": can_view_mappings,
    #     "items": [
    #         {
    #             "label": "Mappings Overview",
    #             "icon": "fas fa-sitemap",
    #             "url_name": "settings_mappings:overview",
    #             "active_names": [("settings_mappings", "overview")],
    #             "icon_classes": "bg-fuchsia-100 text-fuchsia-700 dark:bg-fuchsia-500/10 dark:text-fuchsia-400",
    #         },
    #     ],
    #     "card": True,
    # },
]


def item_is_active(request, item: dict) -> bool:
    resolver_match = getattr(request, "resolver_match", None)
    if not resolver_match:
        return False

    current_namespace = resolver_match.namespace
    current_name = resolver_match.url_name

    for namespace, url_name in item.get("active_names", []):
        if current_namespace == namespace and current_name == url_name:
            return True

    return False


def build_sidebar_menu(request) -> list[dict]:
    user = request.user
    menu = []

    for section in SIDEBAR_MENU:
        if not is_visible(section.get("visible_if"), user):
            continue

        section_items = []

        for item in section.get("items", []):
            if not is_visible(item.get("visible_if"), user):
                continue

            section_items.append(
                {
                    "label": item["label"],
                    "icon": item.get("icon"),
                    "url": safe_reverse(item["url_name"]),
                    "active": item_is_active(request, item),
                    "icon_classes": item.get(
                        "icon_classes",
                        "bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300",
                    ),
                }
            )

        if section_items:
            menu.append(
                {
                    "title": section["title"],
                    "items": section_items,
                    "card": section.get("card", False),
                }
            )

    return menu