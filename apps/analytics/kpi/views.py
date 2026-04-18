from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.urls import reverse
from django.views.generic import TemplateView
from django.contrib.auth.views import redirect_to_login

from apps.analytics.kpi.forms import DashboardFilterForm
from apps.analytics.kpi.services.dashboard_builders import (
    build_daily_occupancy_context,
    build_executive_overview_context,
    build_goals_context,
    build_property_performance_context,
    build_revenue_performance_context,
)
from apps.core.common.access import can_view_dashboard
from apps.core.common.mixins import BreadcrumbMixin


class AnalyticsBaseView(LoginRequiredMixin, BreadcrumbMixin, TemplateView):
    filter_form_class = DashboardFilterForm
    builder = None
    page_title = ''
    analytics_label = ''

    def dispatch(self, request, *args, **kwargs):
        if not can_view_dashboard(request.user):
            # return HttpResponseForbidden('You do not have access to analytics.')
            return redirect_to_login(request.get_full_path(), login_url="login")
        return super().dispatch(request, *args, **kwargs)

    def get_filter_form(self):
        return self.filter_form_class(self.request.GET or None, user=self.request.user)

    def get_breadcrumbs(self):
        return [('Dashboard', reverse('dashboard:home')), ('Analytics', ''), (self.analytics_label or self.page_title, '')]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_form = self.get_filter_form()
        property_obj = start_date = end_date = None
        if filter_form.is_valid():
            property_obj = filter_form.cleaned_data.get('property')
            start_date = filter_form.cleaned_data.get('start_date')
            end_date = filter_form.cleaned_data.get('end_date')
        builder_context = self.builder(self.request.user, property_obj=property_obj, start_date=start_date, end_date=end_date)
        context.update(builder_context)
        context['filter_form'] = filter_form
        context['breadcrumbs'] = self.get_breadcrumbs()
        return context


class ExecutiveOverviewView(AnalyticsBaseView):
    template_name = 'analytics/executive_overview.html'
    builder = staticmethod(build_executive_overview_context)
    analytics_label = 'Executive overview'


class DailyOccupancyView(AnalyticsBaseView):
    template_name = 'analytics/daily_occupancy.html'
    builder = staticmethod(build_daily_occupancy_context)
    analytics_label = 'Daily occupancy'


class RevenuePerformanceView(AnalyticsBaseView):
    template_name = 'analytics/revenue.html'
    builder = staticmethod(build_revenue_performance_context)
    analytics_label = 'Revenue performance'


class PropertyPerformanceView(AnalyticsBaseView):
    template_name = 'analytics/property_performance.html'
    builder = staticmethod(build_property_performance_context)
    analytics_label = 'Property performance'


class GoalsAchievementView(AnalyticsBaseView):
    template_name = 'analytics/goals.html'
    builder = staticmethod(build_goals_context)
    analytics_label = 'Goals & achievements'


from django.shortcuts import render
from urllib.parse import urlencode


def metrics(request):
    active_group = request.GET.get("group", "performance")
    active_period = request.GET.get("period", "FY")
    start_date = request.GET.get("start_date", "")
    end_date = request.GET.get("end_date", "")

    period_options = [
        "1D", "7D", "MTD", "TM" , "LM", "YTD", "YTG", "FY", "LY",  "12M", 
    ]

    dashboard_groups = [
        {
            "key": "performance",
            "label": "Performance",
            "cards": [
                {
                    "card_key": "room_revenue",
                    "card_title": "Room Revenue",
                    "icon_svg": "revenue",
                    "options": [
                        {
                            "key": "revenue",
                            "label": "Revenue",
                            "unit": "currency",
                            "total": 12450000,
                            "budget": 16500000,
                            "forecast": 13800000,
                            "same_time_last_year": 13100000,
                            "last_year_actual": 12650000,
                        },
                        {
                            "key": "revpar",
                            "label": "RevPAR",
                            "unit": "currency",
                            "total": 542.75,
                            "budget": 575.20,
                            "forecast": 558.40,
                            "same_time_last_year": 552.80,
                            "last_year_actual": 548.10,
                        },
                    ],
                },
                {
                    "card_key": "business_volume",
                    "card_title": "Business Volume",
                    "icon_svg": "volume",
                    "options": [
                        {
                            "key": "occupancy",
                            "label": "Occupancy",
                            "unit": "percent",
                            "total": 78.40,
                            "budget": 82.50,
                            "forecast": 80.90,
                            "same_time_last_year": 79.60,
                            "last_year_actual": 79.10,
                        },
                        {
                            "key": "nights",
                            "label": "Nights",
                            "unit": "count",
                            "total": 4832,
                            "budget": 5250,
                            "forecast": 5030,
                            "same_time_last_year": 4920,
                            "last_year_actual": 4885,
                        },
                    ],
                },
                {
                    "card_key": "room_rate",
                    "card_title": "Room Rate",
                    "icon_svg": "rate",
                    "options": [
                        {
                            "key": "adr",
                            "label": "Average Rate",
                            "unit": "currency",
                            "total": 692.35,
                            "budget": 715.00,
                            "forecast": 704.20,
                            "same_time_last_year": 698.80,
                            "last_year_actual": 695.40,
                        }
                    ],
                },
            ],
        }
    ]

    chart_data = {
        "categories": [
            "2025-01-01",
            "2025-01-02",
            "2025-01-03",
            "2025-01-04",
            "2025-01-05",
            "2025-01-06",
            "2025-01-07",
            "2025-01-08",
            "2025-01-09",
            "2025-01-10",
            "2025-01-11",
            "2025-01-12",
            "2025-01-13",
            "2025-01-14",
            "2025-01-15",
            "2025-01-16",
            "2025-01-17",
            "2025-01-18",
            "2025-01-19",
            "2025-01-20",
            "2025-01-21",
            "2025-01-22",
            "2025-01-23",
            "2025-01-24",
            "2025-01-25",
            "2025-01-26",
            "2025-01-27",
            "2025-01-28",
            "2025-01-29",
            "2025-01-30",
            "2025-01-31",
        ],
        "series": {
            "occupancy": [
                72, 73, 71, 74, 75, 76, 74,
                73, 75, 77, 78, 76, 74, 75,
                77, 79, 80, 78, 77, 76, 78,
                79, 81, 80, 78, 77, 79, 80,
                82, 81, 83
            ],
            "revenue": [
                9800000, 9950000, 9700000, 10150000, 10300000, 10420000, 10200000,
                10050000, 10380000, 10650000, 10820000, 10540000, 10360000, 10480000,
                10720000, 11050000, 11200000, 10980000, 10850000, 10700000, 10920000,
                11150000, 11400000, 11320000, 11080000, 10960000, 11250000, 11400000,
                11680000, 11590000, 11850000
            ],
            "adr": [
                628.4, 631.2, 625.8, 636.1, 640.8, 645.0, 639.4,
                634.2, 642.7, 651.4, 659.8, 648.5, 643.0, 646.2,
                654.6, 665.1, 672.4, 666.0, 661.8, 657.1, 663.0,
                671.5, 680.2, 676.8, 669.0, 664.7, 673.4, 679.6,
                688.1, 684.9, 692.4
            ],
            "revpar": [
                452.4, 460.8, 444.3, 470.7, 480.6, 490.2, 472.9,
                463.0, 482.0, 501.6, 514.6, 492.9, 475.8, 484.7,
                504.0, 525.4, 537.9, 519.5, 509.6, 499.4, 517.1,
                530.5, 550.9, 541.4, 521.8, 511.8, 532.0, 543.7,
                564.2, 554.8, 574.7
            ],
            "same_time_last_year": [
                69, 70, 68, 70, 71, 72, 71,
                70, 71, 73, 74, 73, 71, 72,
                73, 75, 76, 75, 74, 73, 74,
                75, 77, 76, 75, 74, 75, 76,
                78, 77, 78
            ]
        }
    }

    groups_map = {group["key"]: group for group in dashboard_groups}
    current_group = groups_map.get(active_group, dashboard_groups[0])

    is_custom_range = bool(start_date and end_date)

    current_state = {
        "group": current_group["key"],
        "period": active_period,
        "start_date": start_date,
        "end_date": end_date,
    }

    for card in current_group["cards"]:
        param_name = f"{card['card_key']}_metric"
        default_option_key = card["options"][0]["key"]
        requested_option_key = request.GET.get(param_name, default_option_key)

        selected_option = next(
            (opt for opt in card["options"] if opt["key"] == requested_option_key),
            card["options"][0],
        )

        card["active_option_key"] = selected_option["key"]
        card["active_option"] = selected_option
        current_state[param_name] = selected_option["key"]

    for card in current_group["cards"]:
        param_name = f"{card['card_key']}_metric"
        for option in card["options"]:
            state_for_option = current_state.copy()
            state_for_option[param_name] = option["key"]
            option["querystring"] = urlencode(state_for_option)

    period_links = []
    for period in period_options:
        state_for_period = current_state.copy()
        state_for_period["period"] = period
        state_for_period["start_date"] = ""
        state_for_period["end_date"] = ""

        period_links.append(
            {
                "label": period,
                "querystring": urlencode(state_for_period),
                "is_active": (period == active_period) and not is_custom_range,
            }
        )

    calendar_querystring = urlencode(current_state)

    context = {
        "groups": dashboard_groups,
        "active_group": current_group["key"],
        "current_group": current_group,
        "active_period": active_period,
        "period_links": period_links,
        "calendar_querystring": calendar_querystring,
        "start_date": start_date,
        "end_date": end_date,
        "is_custom_range": is_custom_range,
        "chart_data_json": chart_data,
    }

    return render(request, "analytics/metrics.html", context)


