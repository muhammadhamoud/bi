from dataclasses import dataclass
from datetime import date

from apps.roi_ingestion.services.missing_detector import MissingFileDetector


@dataclass
class Property:
    id: int
    code: str


def test_missing_file_detection_for_today():
    props = [Property(1, "DXBJV"), Property(2, "AUHAA")]
    missing = MissingFileDetector().detect(
        active_properties=props,
        target_date=date(2026, 4, 22),
        available_file_names={"ROI_DAILY_DXBJV_20260422.XML"},
    )
    assert len(missing) == 1
    assert missing[0].file_name == "ROI_DAILY_AUHAA_20260422.XML"
