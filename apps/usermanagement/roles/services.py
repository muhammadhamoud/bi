from django.contrib.auth.models import Group, Permission

ROLE_ADMIN = 'Admin'
ROLE_MANAGER = 'Manager'
ROLE_OPERATOR = 'Operator'
ROLE_MERCHANT_OWNER = 'Merchant Owner'
ROLE_VIEWER = 'Viewer'

ROLE_PRIORITY = {
    ROLE_VIEWER: 1,
    ROLE_OPERATOR: 2,
    ROLE_MERCHANT_OWNER: 3,
    ROLE_MANAGER: 4,
    ROLE_ADMIN: 5,
}


def get_highest_role(user) -> str:
    if not getattr(user, 'is_authenticated', False):
        return ''
    if user.is_superuser:
        return ROLE_ADMIN
    group_names = list(user.groups.values_list('name', flat=True))
    if not group_names:
        return ROLE_VIEWER
    return max(group_names, key=lambda name: ROLE_PRIORITY.get(name, 0))


def _grant_app_permissions(group: Group, app_labels: list[str], actions: list[str]):
    permissions = Permission.objects.none()
    for action in actions:
        permissions = permissions | Permission.objects.filter(content_type__app_label__in=app_labels, codename__startswith=f'{action}_')
    group.permissions.add(*permissions.distinct())


def _grant_explicit_permissions(group: Group, permission_codes: list[str]):
    for permission_code in permission_codes:
        app_label, codename = permission_code.split('.', 1)
        permission = Permission.objects.filter(content_type__app_label=app_label, codename=codename).first()
        if permission:
            group.permissions.add(permission)


def seed_default_groups():
    groups = {role: Group.objects.get_or_create(name=role)[0] for role in [ROLE_ADMIN, ROLE_MANAGER, ROLE_OPERATOR, ROLE_MERCHANT_OWNER, ROLE_VIEWER]}

    for group in groups.values():
        group.permissions.clear()

    admin = groups[ROLE_ADMIN]
    admin.permissions.set(Permission.objects.all())

    manager = groups[ROLE_MANAGER]
    _grant_app_permissions(manager, ['analyticskpi', 'notificationsinbox', 'powerbiembedded', 'dataopsfiles'], ['view'])
    _grant_app_permissions(manager, ['settingsmappings'], ['view', 'add', 'change'])
    _grant_explicit_permissions(
        manager,
        [
            'propertycore.view_dashboard',
            'propertycore.view_reports',
            'propertycore.view_dataops',
            'propertycore.manage_mappings',
            'usercore.view_user',
            'usercore.add_user',
            'usercore.change_user',
            'profilecore.view_profile',
            'profilecore.change_profile',
            'dataopsfiles.download_filerecord',
        ],
    )

    operator = groups[ROLE_OPERATOR]
    _grant_app_permissions(operator, ['analyticskpi', 'notificationsinbox', 'powerbiembedded', 'dataopsfiles', 'settingsmappings'], ['view'])
    _grant_explicit_permissions(operator, ['propertycore.view_dashboard', 'propertycore.view_reports', 'propertycore.view_dataops'])

    merchant_owner = groups[ROLE_MERCHANT_OWNER]
    _grant_app_permissions(merchant_owner, ['analyticskpi', 'notificationsinbox', 'powerbiembedded', 'dataopsfiles', 'settingsmappings'], ['view'])
    _grant_explicit_permissions(merchant_owner, ['propertycore.view_dashboard', 'propertycore.view_reports', 'propertycore.view_dataops'])

    viewer = groups[ROLE_VIEWER]
    _grant_app_permissions(viewer, ['analyticskpi', 'notificationsinbox', 'powerbiembedded', 'dataopsfiles', 'settingsmappings'], ['view'])
    _grant_explicit_permissions(viewer, ['propertycore.view_dashboard', 'propertycore.view_reports', 'propertycore.view_dataops'])

    return groups
