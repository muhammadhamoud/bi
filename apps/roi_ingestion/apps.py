from django.apps import AppConfig


class RoiIngestionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.roi_ingestion"
    label = "roi_ingestion"
    verbose_name = "ROI Ingestion"
