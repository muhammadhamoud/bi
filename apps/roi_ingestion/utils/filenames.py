import logging
import re
from datetime import date

from .dates import parse_compact_date

logger = logging.getLogger(__name__)

ROI_FILENAME_RE = re.compile(
    r"^(?P<snapshot_name>ROI_DAILY)_(?P<property_code>[A-Z0-9]+)_(?P<snapshot_date>\d{8})\.XML$",
    re.IGNORECASE,
)


def parse_roi_filename(file_name: str) -> dict:
    match = ROI_FILENAME_RE.match(file_name)
    if not match:
        logger.warning("Skipping invalid ROI filename: %s", file_name)
        raise ValueError(f"Invalid ROI filename: {file_name}")

    groups = match.groupdict()
    snapshot_date: date = parse_compact_date(groups["snapshot_date"])
    return {
        "snapshot_name": groups["snapshot_name"].upper(),
        "property_code": groups["property_code"].upper(),
        "snapshot_date": snapshot_date,
        "file_type": "XML",
    }


def expected_roi_file_name(property_code: str, snapshot_date: date) -> str:
    return f"ROI_DAILY_{property_code.upper()}_{snapshot_date:%Y%m%d}.XML"
