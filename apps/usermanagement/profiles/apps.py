from django.apps import AppConfig


class UserManagementProfilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.usermanagement.profiles'
    label = 'profilecore'
    verbose_name = 'Profiles'

    def ready(self):
        import apps.usermanagement.profiles.signals  # noqa: F401
