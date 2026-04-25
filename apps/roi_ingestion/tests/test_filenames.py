from datetime import date
import pytest

from apps.roi_ingestion.utils.filenames import parse_roi_filename


def test_parse_roi_filename_valid():
    parsed = parse_roi_filename("ROI_DAILY_DXBJV_20260422.XML")
    assert parsed == {
        "snapshot_name": "ROI_DAILY",
        "property_code": "DXBJV",
        "snapshot_date": date(2026, 4, 22),
        "file_type": "XML",
    }


def test_parse_roi_filename_invalid():
    with pytest.raises(ValueError):
        parse_roi_filename("BAD_DXBJV_20260422.txt")
