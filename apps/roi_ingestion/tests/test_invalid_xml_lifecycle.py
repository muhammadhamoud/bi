from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

from apps.roi_ingestion.services.ingestion_service import RoiDailyIngestionService


def test_invalid_xml_marks_file_record_failed():
    service = RoiDailyIngestionService(dry_run=False)
    file_record = SimpleNamespace(status="processing", metadata={}, save=lambda **kwargs: None)
    with patch("apps.roi_ingestion.services.ingestion_service.get_file_record_model") as get_model:
        model = SimpleNamespace(LifecycleStatus=SimpleNamespace(FAILED="failed"))
        get_model.return_value = model
        service._mark_failed(file_record, ValueError("invalid xml"))
        assert file_record.status == "failed"
        assert "invalid xml" in file_record.notes
        assert file_record.metadata["error"]["type"] == "ValueError"
