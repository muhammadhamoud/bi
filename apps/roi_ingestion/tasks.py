from dataclasses import asdict
from datetime import date

from celery import shared_task
from celery.schedules import crontab

from .services.ingestion_service import RoiDailyIngestionService


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_kwargs={"max_retries": 3},
)
def ingest_roi_daily_task(
    self,
    target_date: str | None = None,
    property_code: str | None = None,
    force_reload: bool = False,
):
    service = RoiDailyIngestionService()
    parsed_date = date.fromisoformat(target_date) if target_date else None
    result = service.run(
        target_date=parsed_date,
        property_code=property_code,
        force_reload=force_reload,
    )
    return asdict(result)


# Example Celery Beat configuration:
# CELERY_BEAT_SCHEDULE = {
#     "ingest-roi-daily-every-morning-dubai": {
#         "task": "apps.roi_ingestion.tasks.ingest_roi_daily_task",
#         "schedule": crontab(hour=6, minute=30),
#         "args": (),
#     },
# }
