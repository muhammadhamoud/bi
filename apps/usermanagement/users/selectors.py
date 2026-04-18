from django.contrib.auth import get_user_model

from apps.core.common.access import assignable_role_names, get_accessible_properties, get_user_property_ids, user_has_role, user_is_admin
from apps.usermanagement.roles.services import ROLE_ADMIN, ROLE_MANAGER

User = get_user_model()


def get_manageable_users(actor):
    qs = User.objects.prefetch_related('groups', 'property_assignments__property').order_by('email')
    if user_is_admin(actor):
        return qs
    property_ids = get_user_property_ids(actor)
    qs = qs.filter(property_assignments__property_id__in=property_ids).distinct()
    if user_has_role(actor, ROLE_MANAGER):
        return qs.exclude(groups__name__in=[ROLE_ADMIN, ROLE_MANAGER]).distinct()
    return qs.filter(id=actor.id)


def get_assignable_roles(actor):
    return assignable_role_names(actor)


def get_assignable_properties(actor):
    return get_accessible_properties(actor)
