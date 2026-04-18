from django.apps import AppConfig


class UserManagementRolesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.usermanagement.roles'
    label = 'rolecore'
    verbose_name = 'User Roles'
