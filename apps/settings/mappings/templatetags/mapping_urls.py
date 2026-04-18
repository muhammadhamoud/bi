from django import template

register = template.Library()


@register.simple_tag
def append_query(url, query):
    if not query:
        return url
    separator = '&' if '?' in url else '?'
    return f'{url}{separator}{query}'