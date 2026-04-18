from django.apps import AppConfig


class CoreCommonConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core.common'
    label = 'corecommon'
    verbose_name = 'Core Common'
