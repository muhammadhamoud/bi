from unittest.mock import patch

from django.core.management import call_command


def test_management_command_dry_run():
    with patch("apps.roi_ingestion.management.commands.ingest_roi_daily.RoiDailyIngestionService") as service_cls:
        service = service_cls.return_value
        service.run.return_value.files_found = 0
        call_command("ingest_roi_daily", "--today", "--dry-run")
        service_cls.assert_called_once()
        assert service_cls.call_args.kwargs["dry_run"] is True
        service.run.assert_called_once()
