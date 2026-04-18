from django.apps import AppConfig


class DataOpsFilesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.dataops.files'
    label = 'dataopsfiles'
    verbose_name = 'Data Operations'
