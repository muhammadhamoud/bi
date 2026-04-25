from dataclasses import dataclass
from datetime import date
from typing import Iterable

from apps.roi_ingestion.utils.filenames import expected_roi_file_name


@dataclass(frozen=True)
class ExpectedMissingFile:
    property_obj: object
    property_code: str
    expected_date: date
    file_name: str


class MissingFileDetector:
    def detect(
        self,
        *,
        active_properties: Iterable[object],
        target_date: date,
        available_file_names: set[str],
    ) -> list[ExpectedMissingFile]:
        missing: list[ExpectedMissingFile] = []
        available_upper = {name.upper() for name in available_file_names}
        for property_obj in active_properties:
            property_code = str(getattr(property_obj, "code")).upper()
            file_name = expected_roi_file_name(property_code, target_date)
            if file_name.upper() not in available_upper:
                missing.append(
                    ExpectedMissingFile(
                        property_obj=property_obj,
                        property_code=property_code,
                        expected_date=target_date,
                        file_name=file_name,
                    )
                )
        return missing
