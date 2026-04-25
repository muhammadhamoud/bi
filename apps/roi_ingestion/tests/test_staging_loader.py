from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from apps.roi_ingestion.services.roi_xml_parser import ParsedDailyDetail, ParsedReservation
from apps.roi_ingestion.services.staging_loader import RoiStagingLoader


def _reservation():
    return ParsedReservation(
        property_code="DXBJV",
        snapshot_name="ROI_DAILY",
        snapshot_date=date(2026, 4, 22),
        business_date=date(2026, 4, 22),
        resort="DXBJV",
        currency_code="AED",
        integration_id="202601",
        arrival_date=date(2024, 11, 1),
        status="CANCELLED",
        reservation_id="50059",
        details_raw="raw",
        details_json={"name_id": "1"},
        daily_details=[ParsedDailyDetail("RDEN_CODES", 0, "0|A", {"day_offset": "0"}, "detailhash")],
        row_hash="reshash",
        metadata={},
    )


@patch("apps.roi_ingestion.services.staging_loader.RoiReservationDailyStage.objects")
@patch("apps.roi_ingestion.services.staging_loader.RoiReservationStage.objects")
def test_staging_loader_bulk_insert_uses_alias(res_objects, detail_objects):
    res_manager = MagicMock()
    detail_manager = MagicMock()
    res_objects.using.return_value = res_manager
    detail_objects.using.return_value = detail_manager
    loader = RoiStagingLoader(batch_size=1, using="roi_staging")
    file_record = SimpleNamespace(id=10, file_name="ROI_DAILY_DXBJV_20260422.XML")
    property_obj = SimpleNamespace(id=20)
    counts = loader.load_file(
        file_record=file_record,
        property_obj=property_obj,
        source_system_code="ROI_DAILY",
        parsed_reservations=[_reservation()],
    )
    assert counts == (1, 1)
    res_objects.using.assert_called_with("roi_staging")
    detail_objects.using.assert_called_with("roi_staging")
    assert res_manager.bulk_create.call_args.kwargs["ignore_conflicts"] is True
    assert detail_manager.bulk_create.call_args.kwargs["ignore_conflicts"] is True
