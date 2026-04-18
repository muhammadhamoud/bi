# from django import template

# register = template.Library()


# def _to_float(value):
#     try:
#         return float(value)
#     except (TypeError, ValueError):
#         return 0.0


# @register.filter
# def compact_number(value, decimals=2):
#     value = _to_float(value)
#     decimals = int(decimals)
#     abs_value = abs(value)
#     sign = "-" if value < 0 else ""

#     if abs_value < 10_000:
#         if value.is_integer():
#             return f"{value:,.0f}"
#         return f"{value:,.{decimals}f}"

#     if abs_value >= 1_000_000_000:
#         return f"{sign}{abs_value / 1_000_000_000:.{decimals}f}B"
#     if abs_value >= 1_000_000:
#         return f"{sign}{abs_value / 1_000_000:.{decimals}f}M"
#     return f"{sign}{abs_value / 1_000:.{decimals}f}K"


# @register.filter
# def signed_pct_2(value):
#     value = _to_float(value)
#     sign = "+" if value > 0 else ""
#     return f"{sign}{value:.1f}%"


# @register.filter
# def trend_arrow(value):
#     return "▲" if _to_float(value) >= 0 else "▼"


# @register.filter
# def trend_color(value):
#     return "text-emerald-300" if _to_float(value) >= 0 else "text-rose-300"


# @register.simple_tag
# def percent_change(current, reference):
#     current = _to_float(current)
#     reference = _to_float(reference)
#     if reference == 0:
#         return 0
#     return ((current - reference) / reference) * 100


# @register.simple_tag
# def compare_progress(current, reference):
#     current = _to_float(current)
#     reference = _to_float(reference)

#     if reference <= 0:
#         return 0

#     return min((current / reference) * 100, 100)


from django import template
import math

register = template.Library()


def _to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


@register.filter
def compact_number(value, decimals=2):
    value = _to_float(value)
    decimals = int(decimals)
    abs_value = abs(value)
    sign = "-" if value < 0 else ""

    if abs_value < 10_000:
        if value.is_integer():
            return f"{value:,.0f}"
        return f"{value:,.{decimals}f}"

    if abs_value >= 1_000_000_000:
        return f"{sign}{abs_value / 1_000_000_000:.{decimals}f}B"
    if abs_value >= 1_000_000:
        return f"{sign}{abs_value / 1_000_000:.{decimals}f}M"
    return f"{sign}{abs_value / 1_000:.{decimals}f}K"


@register.filter
def signed_pct_1(value):
    value = _to_float(value)
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.1f}%"


@register.filter
def trend_arrow(value):
    return "▲" if _to_float(value) >= 0 else "▼"


@register.filter
def trend_color(value):
    return "text-emerald-300" if _to_float(value) >= 0 else "text-rose-300"


@register.filter
def metric_value(value, unit="currency"):
    """
    Formatting rules:
    - percent values like occupancy => 0 decimals, rounded up
    - currency/count values < 10,000 => regular comma formatting
    - currency values < 100 => 1 decimal (good for ADR small values)
    - larger values => compact K / M / B
    """
    value = _to_float(value)
    abs_value = abs(value)

    if unit == "percent":
        return f"{math.ceil(value):,.0f}%"

    if abs_value < 100:
        return f"{value:,.1f}"

    if abs_value < 10_000:
        if value.is_integer():
            return f"{value:,.0f}"
        return f"{value:,.0f}"

    return compact_number(value, 2)


@register.simple_tag
def percent_change(current, reference):
    current = _to_float(current)
    reference = _to_float(reference)
    if reference == 0:
        return 0
    return ((current - reference) / reference) * 100


@register.simple_tag
def compare_progress(current, reference):
    current = _to_float(current)
    reference = _to_float(reference)

    if reference <= 0:
        return 0

    return min((current / reference) * 100, 100)