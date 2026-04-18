from django import template

from apps.analytics.kpi.services.kpi_calculations import format_compact, format_currency, format_percentage, trend_state

register = template.Library()


@register.filter
def percentage(value, places=1):
    return format_percentage(value, int(places))


@register.filter
def currency(value, currency_code='AED'):
    return format_currency(value, currency_code)


@register.filter
def compact_number(value, places=1):
    return format_compact(value, int(places))


@register.filter
def trend(value):
    return trend_state(value)
