from django.apps import AppConfig


class UserManagementUsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.usermanagement.users'
    label = 'usercore'
    verbose_name = 'Users'
