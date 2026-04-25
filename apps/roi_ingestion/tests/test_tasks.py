from unittest.mock import patch

from apps.roi_ingestion.tasks import ingest_roi_daily_task


def test_celery_task_calling_service():
    with patch("apps.roi_ingestion.tasks.RoiDailyIngestionService") as service_cls:
        service = service_cls.return_value
        service.run.return_value.files_found = 1
        result = ingest_roi_daily_task.run(target_date="2026-04-22", property_code="DXBJV")
        service.run.assert_called_once()
        assert result["files_found"] == 1
