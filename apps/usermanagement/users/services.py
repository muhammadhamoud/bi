from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from apps.usermanagement.users.models import UserPropertyAccess

User = get_user_model()


def sync_user_role(user: User, role_name: str | None):
    if not role_name:
        user.groups.clear()
        return user
    group = Group.objects.filter(name=role_name).first()
    if group:
        user.groups.set([group])
    return user


def sync_user_properties(user: User, properties, assigned_by=None):
    properties = list(properties)
    property_ids = {prop.id for prop in properties}
    existing = {assignment.property_id: assignment for assignment in user.property_assignments.all()}

    for property_id, assignment in existing.items():
        if property_id not in property_ids:
            assignment.delete()

    for property_obj in properties:
        assignment, created = UserPropertyAccess.objects.get_or_create(
            user=user,
            property=property_obj,
            defaults={'assigned_by': assigned_by, 'is_primary': False},
        )
        if created and assigned_by:
            assignment.assigned_by = assigned_by
            assignment.save(update_fields=['assigned_by'])

    primary_assignment = user.property_assignments.order_by('-is_primary', 'created_at').first()
    if primary_assignment and not user.property_assignments.filter(is_primary=True).exists():
        primary_assignment.is_primary = True
        primary_assignment.save(update_fields=['is_primary'])
    return user
