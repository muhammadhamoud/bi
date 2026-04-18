from django import template

from apps.core.common.access import user_has_any_role, user_has_role

register = template.Library()


@register.filter
def has_role(user, role_name):
    return user_has_role(user, role_name)


@register.filter
def has_any_role(user, role_names_csv):
    role_names = [role.strip() for role in role_names_csv.split(',') if role.strip()]
    return user_has_any_role(user, role_names)


@register.simple_tag(takes_context=True)
def is_active_path(context, prefix):
    request = context['request']
    return request.path.startswith(prefix)
