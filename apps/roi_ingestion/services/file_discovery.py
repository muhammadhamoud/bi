from dataclasses import dataclass
from datetime import date
import logging

from apps.roi_ingestion.utils.filenames import parse_roi_filename

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RoiFileDescriptor:
    file_name: str
    snapshot_name: str
    property_code: str
    snapshot_date: date
    file_type: str
    size_bytes: int | None = None
    remote_path: str | None = None


@dataclass
class RoiFileDiscoveryResult:
    valid_files: list[RoiFileDescriptor]
    invalid_files: list[str]


class RoiFileDiscoveryService:
    def discover(
        self,
        remote_files: list[str],
        *,
        file_sizes: dict[str, int] | None = None,
        property_code: str | None = None,
        target_date: date | None = None,
        process_older_unloaded: bool = True,
    ) -> RoiFileDiscoveryResult:
        valid: list[RoiFileDescriptor] = []
        invalid: list[str] = []
        normalized_property_code = property_code.upper() if property_code else None
        file_sizes = file_sizes or {}

        for file_name in remote_files:
            try:
                parsed = parse_roi_filename(file_name)
            except ValueError:
                invalid.append(file_name)
                continue

            if normalized_property_code and parsed["property_code"] != normalized_property_code:
                continue
            if target_date and not process_older_unloaded and parsed["snapshot_date"] != target_date:
                continue
            if target_date and process_older_unloaded and parsed["snapshot_date"] > target_date:
                continue

            valid.append(
                RoiFileDescriptor(
                    file_name=file_name,
                    snapshot_name=parsed["snapshot_name"],
                    property_code=parsed["property_code"],
                    snapshot_date=parsed["snapshot_date"],
                    file_type=parsed["file_type"],
                    size_bytes=file_sizes.get(file_name),
                )
            )
        valid.sort(key=lambda item: (item.snapshot_date, item.property_code, item.file_name))
        return RoiFileDiscoveryResult(valid_files=valid, invalid_files=invalid)
