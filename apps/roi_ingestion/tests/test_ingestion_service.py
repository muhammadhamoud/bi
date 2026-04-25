from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from apps.roi_ingestion.services.file_discovery import RoiFileDescriptor
from apps.roi_ingestion.services.ingestion_service import RoiDailyIngestionService


def test_force_reload_processes_loaded_file():
    service = RoiDailyIngestionService(dry_run=True)
    loaded_record = SimpleNamespace(status="loaded")
    with patch("apps.roi_ingestion.services.ingestion_service.get_file_record_model") as get_model:
        model = MagicMock()
        model.LifecycleStatus.LOADED = "loaded"
        get_model.return_value = model
        assert service._status_is(loaded_record, "LOADED", "loaded") is True


def test_idempotent_file_record_creation_uses_get_or_create():
    service = RoiDailyIngestionService(dry_run=True)
    source = SimpleNamespace(id=1)
    prop = SimpleNamespace(id=2)
    descriptor = RoiFileDescriptor("ROI_DAILY_DXBJV_20260422.XML", "ROI_DAILY", "DXBJV", date(2026, 4, 22), "XML")
    existing = {}
    with patch("apps.roi_ingestion.services.ingestion_service.get_file_record_model") as get_model:
        manager = MagicMock()
        model = MagicMock()
        model.objects.using.return_value = manager
        manager.get_or_create.return_value = (SimpleNamespace(id=99, file_name=descriptor.file_name), True)
        get_model.return_value = model
        record = service._get_or_create_file_record(source_system=source, property_obj=prop, descriptor=descriptor, existing=existing)
        assert record.id == 99
        manager.get_or_create.assert_called_once()
