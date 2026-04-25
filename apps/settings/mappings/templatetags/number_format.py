from django import template

register = template.Library()


@register.filter
def compact_number(value):
    try:
        num = float(value)
    except (TypeError, ValueError):
        return value

    abs_num = abs(num)

    if abs_num >= 1_000_000_000:
        formatted = num / 1_000_000_000
        suffix = 'B'
    elif abs_num >= 1_000_000:
        formatted = num / 1_000_000
        suffix = 'M'
    elif abs_num >= 1_000:
        formatted = num / 1_000
        suffix = 'K'
    else:
        return str(int(num)) if num == int(num) else str(num)

    if formatted == int(formatted):
        return f'{int(formatted)}{suffix}'
    return f'{formatted:.1f}{suffix}'