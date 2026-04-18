from __future__ import annotations

from decimal import Decimal, InvalidOperation


def _to_decimal(value) -> Decimal:
    if value in (None, ''):
        return Decimal('0')
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return Decimal('0')


def safe_divide(numerator, denominator, default=Decimal('0')):
    numerator = _to_decimal(numerator)
    denominator = _to_decimal(denominator)
    if denominator == 0:
        return _to_decimal(default)
    return numerator / denominator


def occupancy(rooms_sold, available_rooms):
    return safe_divide(rooms_sold, available_rooms) * Decimal('100')


def adr(room_revenue, rooms_sold):
    return safe_divide(room_revenue, rooms_sold)


def revpar(room_revenue, available_rooms):
    return safe_divide(room_revenue, available_rooms)


def percentage_change(current_value, previous_value):
    current_value = _to_decimal(current_value)
    previous_value = _to_decimal(previous_value)
    if previous_value == 0:
        return Decimal('0')
    return ((current_value - previous_value) / previous_value) * Decimal('100')


def absolute_change(current_value, previous_value):
    return _to_decimal(current_value) - _to_decimal(previous_value)


def achieved_goal_percentage(actual_value, goal_value):
    return safe_divide(actual_value, goal_value) * Decimal('100')


def format_percentage(value, places=1):
    return f'{_to_decimal(value):,.{places}f}%'


def format_currency(value, currency='AED', places=0):
    return f'{currency} {_to_decimal(value):,.{places}f}'


def format_compact(value, places=1):
    value = float(_to_decimal(value))
    suffixes = [(1_000_000_000, 'B'), (1_000_000, 'M'), (1_000, 'K')]
    for factor, suffix in suffixes:
        if abs(value) >= factor:
            return f'{value / factor:.{places}f}{suffix}'
    return f'{value:,.{places}f}'


def trend_state(delta_value):
    delta = _to_decimal(delta_value)
    if delta > 0:
        return 'positive'
    if delta < 0:
        return 'negative'
    return 'neutral'
