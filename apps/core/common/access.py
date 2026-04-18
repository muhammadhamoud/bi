from __future__ import annotations

from typing import Iterable

from django.db.models import QuerySet

from apps.usermanagement.roles.services import (
    ROLE_ADMIN,
    ROLE_MANAGER,
    ROLE_MERCHANT_OWNER,
    ROLE_OPERATOR,
    ROLE_VIEWER,
    get_highest_role,
)


ALL_ROLE_NAMES = [ROLE_ADMIN, ROLE_MANAGER, ROLE_OPERATOR, ROLE_MERCHANT_OWNER, ROLE_VIEWER]


def user_group_names(user) -> list[str]:
    if not getattr(user, 'is_authenticated', False):
        return []
    return list(user.groups.values_list('name', flat=True))


def user_has_role(user, role_name: str) -> bool:
    return getattr(user, 'is_authenticated', False) and (user.is_superuser or user.groups.filter(name=role_name).exists())


def user_has_any_role(user, role_names: Iterable[str]) -> bool:
    role_names = list(role_names)
    if not getattr(user, 'is_authenticated', False):
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=role_names).exists()


def user_is_admin(user) -> bool:
    return user_has_role(user, ROLE_ADMIN)


def can_manage_users(user) -> bool:
    return user_is_admin(user) or user_has_role(user, ROLE_MANAGER)


def can_manage_mappings(user) -> bool:
    return user_is_admin(user) or user_has_role(user, ROLE_MANAGER)


def can_view_dashboard(user) -> bool:
    return getattr(user, 'is_authenticated', False)


def can_view_reports(user) -> bool:
    return getattr(user, 'is_authenticated', False) and (
        user_is_admin(user)
        or user.has_perm('propertycore.view_reports')
        or user_has_any_role(user, ALL_ROLE_NAMES)
    )


def can_view_dataops(user) -> bool:
    return getattr(user, 'is_authenticated', False) and (
        user_is_admin(user)
        or user.has_perm('propertycore.view_dataops')
        or user_has_any_role(user, ALL_ROLE_NAMES)
    )


def can_download_files(user) -> bool:
    return can_view_dataops(user) and (
        user_is_admin(user) or user.has_perm('dataopsfiles.download_filerecord')
    )


def can_view_mappings(user) -> bool:
    return getattr(user, 'is_authenticated', False) and (
        can_manage_mappings(user) or user_has_any_role(user, ALL_ROLE_NAMES)
    )


def get_user_property_ids(user) -> list[int]:
    if not getattr(user, 'is_authenticated', False):
        return []
    from apps.properties.core.models import Property

    if user_is_admin(user):
        return list(Property.objects.filter(is_active=True).values_list('id', flat=True))
    return list(
        user.property_assignments.filter(is_active=True, property__is_active=True).values_list('property_id', flat=True)
    )


def get_accessible_properties(user):
    from apps.properties.core.models import Property

    if not getattr(user, 'is_authenticated', False):
        return Property.objects.none()
    if user_is_admin(user):
        return Property.objects.filter(is_active=True).select_related('organization')
    return Property.objects.filter(assignments__user=user, assignments__is_active=True, is_active=True).select_related('organization').distinct()


def filter_queryset_for_user(qs: QuerySet, user, property_lookup: str = 'property') -> QuerySet:
    if user_is_admin(user):
        return qs
    property_ids = get_user_property_ids(user)
    if not property_ids:
        return qs.none()
    return qs.filter(**{f'{property_lookup}__in': property_ids}).distinct()


def get_current_property(request, user=None, properties_qs=None):
    user = user or getattr(request, 'user', None)
    if not getattr(user, 'is_authenticated', False):
        return None
    properties_qs = properties_qs or get_accessible_properties(user)
    current_property_id = request.session.get('current_property_id')
    if current_property_id:
        current = properties_qs.filter(id=current_property_id).first()
        if current:
            return current
    current = properties_qs.first()
    if current:
        request.session['current_property_id'] = current.id
    return current


def assignable_role_names(actor) -> list[str]:
    if user_is_admin(actor):
        return ALL_ROLE_NAMES
    if user_has_role(actor, ROLE_MANAGER):
        return [ROLE_OPERATOR, ROLE_MERCHANT_OWNER, ROLE_VIEWER]
    return []


def actor_highest_role(actor) -> str:
    return get_highest_role(actor)



from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden


class SuperuserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(self.request.get_full_path(), login_url="login")
        return HttpResponseForbidden("You do not have permission to access this page.")