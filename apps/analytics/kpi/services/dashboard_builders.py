from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone

from apps.analytics.kpi.models import PropertyDailyMetric
from apps.analytics.kpi.services.kpi_calculations import (
    absolute_change,
    achieved_goal_percentage,
    adr,
    format_compact,
    format_currency,
    format_percentage,
    occupancy,
    percentage_change,
    revpar,
    trend_state,
)
from apps.core.common.access import can_view_dataops, can_view_reports, filter_queryset_for_user, get_current_property
from apps.notifications.announcements.models import Announcement
from apps.notifications.inbox.models import Notification
from apps.powerbi.embedded.selectors import get_accessible_reports
from apps.dataops.files.selectors import accessible_event_logs


def _date_bounds(start_date=None, end_date=None, default_days=30):
    today = timezone.localdate()
    end_date = end_date or today
    start_date = start_date or (end_date - timedelta(days=default_days - 1))
    return start_date, end_date


def _base_queryset(user, property_obj=None, start_date=None, end_date=None):
    start_date, end_date = _date_bounds(start_date, end_date)
    qs = PropertyDailyMetric.objects.select_related('property').filter(metric_date__range=(start_date, end_date))
    qs = filter_queryset_for_user(qs, user)
    if property_obj:
        qs = qs.filter(property=property_obj)
    return qs.order_by('metric_date')


# def _aggregate(qs):
#     return qs.aggregate(
#         available_rooms=Coalesce(Sum('available_rooms'), 0),
#         rooms_sold=Coalesce(Sum('rooms_sold'), 0),
#         room_revenue=Coalesce(Sum('room_revenue'), 0),
#         total_revenue=Coalesce(Sum('total_revenue'), 0),
#         revenue_goal=Coalesce(Sum('revenue_goal'), 0),
#     )


from django.db.models import Sum, Value, DecimalField, IntegerField
from django.db.models.functions import Coalesce


def _aggregate(qs):
    return qs.aggregate(
        available_rooms=Coalesce(
            Sum("available_rooms"),
            Value(0, output_field=IntegerField()),
        ),
        rooms_sold=Coalesce(
            Sum("rooms_sold"),
            Value(0, output_field=IntegerField()),
        ),
        room_revenue=Coalesce(
            Sum("room_revenue"),
            Value(0, output_field=DecimalField(max_digits=14, decimal_places=2)),
        ),
        total_revenue=Coalesce(
            Sum("total_revenue"),
            Value(0, output_field=DecimalField(max_digits=14, decimal_places=2)),
        ),
        revenue_goal=Coalesce(
            Sum("revenue_goal"),
            Value(0, output_field=DecimalField(max_digits=14, decimal_places=2)),
        ),
    )


def _previous_period_qs(user, property_obj, start_date, end_date):
    span = (end_date - start_date).days + 1
    previous_end = start_date - timedelta(days=1)
    previous_start = previous_end - timedelta(days=span - 1)
    return _base_queryset(user, property_obj=property_obj, start_date=previous_start, end_date=previous_end)


def _card(title, raw_value, display_value, delta_value, subtitle, icon='•'):
    return {
        'title': title,
        'raw_value': float(raw_value) if isinstance(raw_value, Decimal) else raw_value,
        'value': display_value,
        'delta': float(delta_value) if isinstance(delta_value, Decimal) else delta_value,
        'trend': trend_state(delta_value),
        'subtitle': subtitle,
        'icon': icon,
    }


def _chart_config(chart_type, labels, data, label, y_suffix=''):
    return {
        'type': chart_type,
        'data': {
            'labels': labels,
            'datasets': [
                {
                    'label': label,
                    'data': data,
                    'borderWidth': 2,
                    'tension': 0.35,
                }
            ],
        },
        'options': {
            'responsive': True,
            'maintainAspectRatio': False,
            'scales': {
                'y': {'beginAtZero': True}
            },
            'plugins': {
                'legend': {'display': True, 'position': 'bottom'},
            },
        },
    }


def build_executive_overview_context(user, property_obj=None, start_date=None, end_date=None):
    start_date, end_date = _date_bounds(start_date, end_date)
    qs = _base_queryset(user, property_obj=property_obj, start_date=start_date, end_date=end_date)
    current = _aggregate(qs)
    previous = _aggregate(_previous_period_qs(user, property_obj, start_date, end_date))

    current_occupancy = occupancy(current['rooms_sold'], current['available_rooms'])
    previous_occupancy = occupancy(previous['rooms_sold'], previous['available_rooms'])
    current_adr = adr(current['room_revenue'], current['rooms_sold'])
    previous_adr = adr(previous['room_revenue'], previous['rooms_sold'])
    current_revpar = revpar(current['room_revenue'], current['available_rooms'])
    previous_revpar = revpar(previous['room_revenue'], previous['available_rooms'])
    goal_pct = achieved_goal_percentage(current['total_revenue'], current['revenue_goal'])

    cards = [
        _card('Total Revenue', current['total_revenue'], format_currency(current['total_revenue']), percentage_change(current['total_revenue'], previous['total_revenue']), 'MTD vs prior period', '$'),
        _card('Occupancy', current_occupancy, format_percentage(current_occupancy), absolute_change(current_occupancy, previous_occupancy), 'Rooms sold / available rooms', '%'),
        _card('ADR', current_adr, format_currency(current_adr), percentage_change(current_adr, previous_adr), 'Average daily rate', 'D'),
        _card('RevPAR', current_revpar, format_currency(current_revpar), percentage_change(current_revpar, previous_revpar), 'Revenue per available room', 'R'),
        _card('Rooms Sold', current['rooms_sold'], format_compact(current['rooms_sold'], 0), absolute_change(current['rooms_sold'], previous['rooms_sold']), 'Period total', '□'),
        _card('Available Rooms', current['available_rooms'], format_compact(current['available_rooms'], 0), absolute_change(current['available_rooms'], previous['available_rooms']), 'Inventory base', '▣'),
        _card('Goal Achievement', goal_pct, format_percentage(goal_pct), absolute_change(current['total_revenue'], current['revenue_goal']), 'Actual versus revenue goal', '◎'),
    ]

    daily_labels = [item.metric_date.strftime('%d %b') for item in qs]
    occupancy_series = [float(occupancy(item.rooms_sold, item.available_rooms)) for item in qs]
    revenue_series = [float(item.total_revenue) for item in qs]

    insights = [
        f'Occupancy closed at {format_percentage(current_occupancy)} over the selected range.',
        f'ADR delivered {format_currency(current_adr)} and RevPAR landed at {format_currency(current_revpar)}.',
        f'Revenue reached {format_percentage(goal_pct)} of target for the period.',
    ]

    return {
        'page_title': 'Executive overview',
        'cards': cards,
        'insights': insights,
        'occupancy_chart': _chart_config('line', daily_labels, occupancy_series, 'Daily occupancy'),
        'revenue_chart': _chart_config('bar', daily_labels, revenue_series, 'Daily revenue'),
        'current_period': {'start_date': start_date, 'end_date': end_date},
        'current_property': property_obj,
    }


def build_daily_occupancy_context(user, property_obj=None, start_date=None, end_date=None):
    context = build_executive_overview_context(user, property_obj, start_date, end_date)
    context['page_title'] = 'Daily occupancy dashboard'
    context['primary_chart'] = context['occupancy_chart']
    return context


def build_revenue_performance_context(user, property_obj=None, start_date=None, end_date=None):
    context = build_executive_overview_context(user, property_obj, start_date, end_date)
    context['page_title'] = 'Revenue performance dashboard'
    context['primary_chart'] = context['revenue_chart']
    return context


def build_property_performance_context(user, property_obj=None, start_date=None, end_date=None):
    start_date, end_date = _date_bounds(start_date, end_date)
    qs = _base_queryset(user, property_obj=property_obj, start_date=start_date, end_date=end_date)
    table = []
    comparison_labels = []
    comparison_values = []
    for property_name in qs.values_list('property__name', flat=True).distinct():
        subset = qs.filter(property__name=property_name)
        agg = _aggregate(subset)
        occ = occupancy(agg['rooms_sold'], agg['available_rooms'])
        current_adr = adr(agg['room_revenue'], agg['rooms_sold'])
        current_revpar = revpar(agg['room_revenue'], agg['available_rooms'])
        row = {
            'property_name': property_name,
            'occupancy': format_percentage(occ),
            'adr': format_currency(current_adr),
            'revpar': format_currency(current_revpar),
            'revenue': format_currency(agg['total_revenue']),
        }
        table.append(row)
        comparison_labels.append(property_name)
        comparison_values.append(float(agg['total_revenue']))
    return {
        'page_title': 'Property performance dashboard',
        'comparison_table': table,
        'comparison_chart': _chart_config('bar', comparison_labels, comparison_values, 'Revenue by property'),
        'current_period': {'start_date': start_date, 'end_date': end_date},
        'current_property': property_obj,
    }


def build_goals_context(user, property_obj=None, start_date=None, end_date=None):
    start_date, end_date = _date_bounds(start_date, end_date)
    qs = _base_queryset(user, property_obj=property_obj, start_date=start_date, end_date=end_date)
    agg = _aggregate(qs)
    goal_pct = achieved_goal_percentage(agg['total_revenue'], agg['revenue_goal'])
    return {
        'page_title': 'Goals and achievements dashboard',
        'goal_cards': [
            _card('Revenue Goal', agg['revenue_goal'], format_currency(agg['revenue_goal']), 0, 'Configured goal', 'G'),
            _card('Actual Revenue', agg['total_revenue'], format_currency(agg['total_revenue']), absolute_change(agg['total_revenue'], agg['revenue_goal']), 'Period actual', 'A'),
            _card('Achieved %', goal_pct, format_percentage(goal_pct), goal_pct - Decimal('100'), 'Goal completion', '%'),
        ],
        'goal_chart': {
            'type': 'bar',
            'data': {
                'labels': ['Target', 'Actual'],
                'datasets': [{'label': 'Goal comparison', 'data': [float(agg['revenue_goal']), float(agg['total_revenue'])], 'borderWidth': 1}],
            },
            'options': {'responsive': True, 'maintainAspectRatio': False, 'plugins': {'legend': {'display': False}}},
        },
        'current_period': {'start_date': start_date, 'end_date': end_date},
        'current_property': property_obj,
    }


def build_home_dashboard_context(user, request=None):
    property_obj = get_current_property(request, user) if request else None
    overview = build_executive_overview_context(user, property_obj=property_obj)
    quick_links = [
        {'title': 'Executive overview', 'url_name': 'analytics:executive'},
        {'title': 'Daily occupancy', 'url_name': 'analytics:occupancy'},
        {'title': 'Revenue performance', 'url_name': 'analytics:revenue'},
        {'title': 'Property performance', 'url_name': 'analytics:properties'},
        {'title': 'Goals & achievements', 'url_name': 'analytics:goals'},
    ]
    if can_view_reports(user):
        quick_links.append({'title': 'Embedded reports', 'url_name': 'powerbi:group-list'})
    if can_view_dataops(user):
        quick_links.append({'title': 'Data operations', 'url_name': 'dataops:dashboard'})

    report_shortcuts = get_accessible_reports(user)[:4]
    notifications = Notification.objects.filter(recipient=user).order_by('-created_at')[:5]
    activity = accessible_event_logs(user).order_by('-created_at')[:5]
    announcements = Announcement.objects.filter(is_published=True).filter_active(now=timezone.now())[:3]

    return {
        'home_cards': overview['cards'][:4],
        'home_occupancy_chart': overview['occupancy_chart'],
        'home_revenue_chart': overview['revenue_chart'],
        'quick_links': quick_links,
        'report_shortcuts': report_shortcuts,
        'recent_notifications': notifications,
        'recent_activity': activity,
        'recent_announcements': [item for item in announcements if item.is_visible_to_user(user)],
        'insights': overview['insights'],
    }
