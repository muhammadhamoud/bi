from __future__ import annotations

from typing import Callable, Optional

from django.urls import NoReverseMatch, reverse

from apps.core.common.access import (
    can_manage_users,
    can_view_mappings,
    can_view_reports,
)


def safe_reverse(url_name: str | None = None, **kwargs) -> str:
    if not url_name:
        return "#"
    try:
        return reverse(url_name, kwargs=kwargs)
    except NoReverseMatch:
        return "#"


def is_visible(check: Optional[Callable[[object], bool]], user) -> bool:
    if check is None:
        return True
    return check(user)


HEADER_MENU = [
    {
        "key": "reports",
        "type": "hover_dropdown",
        "label": "Reports",
        "icon": "fas fa-chart-line",
        "visible_if": can_view_reports,
        "items_var": "report_menu",
        "trigger_classes": (
            "inline-flex items-center gap-2 rounded-xl px-4 py-2 "
            "text-sm font-medium text-slate-700 transition "
            "hover:bg-slate-100 hover:text-slate-900 "
            "dark:text-slate-200 dark:hover:bg-slate-800 dark:hover:text-white"
        ),
    },
    {
        "key": "announcements",
        "type": "custom",
        "component": "announcements_icon",
    },
    {
        "key": "notifications",
        "type": "custom",
        "component": "notifications_menu",
    },

    {
        "key": "property_switcher",
        "type": "custom",
        "component": "property_switcher",
    },
    {
        "key": "theme_toggle",
        "type": "custom",
        "component": "theme_toggle",
    },
    {
        "key": "settings",
        "type": "icon_link",
        "label": "Settings",
        "icon": "fas fa-cog",
        "url_name": "settings_mappings:overview",
        "visible_if": can_view_mappings,
    },
    {
        "key": "user_menu",
        "type": "custom",
        "component": "user_menu",
    },
]


def build_header_menu(request) -> list[dict]:
    user = request.user
    items: list[dict] = []

    for item in HEADER_MENU:
        if not is_visible(item.get("visible_if"), user):
            continue

        prepared = {
            "key": item["key"],
            "type": item["type"],
            "label": item.get("label"),
            "icon": item.get("icon"),
            "url": safe_reverse(item.get("url_name")) if item.get("url_name") else None,
            "component": item.get("component"),
            "items_var": item.get("items_var"),
            "trigger_classes": item.get("trigger_classes", ""),
            "button_classes": item.get(
                "button_classes",
                "inline-flex items-center gap-2 rounded-xl border border-slate-200 "
                "bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm "
                "transition hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 "
                "dark:text-slate-200 dark:hover:bg-slate-800",
            ),
            "link_classes": item.get(
                "link_classes",
                "inline-flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium "
                "text-slate-700 transition hover:bg-slate-100 hover:text-slate-900 "
                "dark:text-slate-200 dark:hover:bg-slate-800 dark:hover:text-white",
            ),
        }
        items.append(prepared)

    return items