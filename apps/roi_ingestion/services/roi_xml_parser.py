from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterator
import logging

from apps.roi_ingestion.constants import DAILY_HEADERS, RESERVATION_DETAILS_HEADERS
from apps.roi_ingestion.utils.dates import parse_iso_date
from apps.roi_ingestion.utils.delimited import parse_compound_records, parse_pipe_record
from apps.roi_ingestion.utils.hashing import stable_hash_dict

logger = logging.getLogger(__name__)

try:
    from lxml import etree as ET  # type: ignore
except ImportError:  # pragma: no cover
    import xml.etree.ElementTree as ET  # type: ignore


@dataclass(frozen=True)
class RoiFileContext:
    file_name: str
    snapshot_name: str
    property_code: str
    snapshot_date: date
    file_type: str


@dataclass
class ParsedDailyDetail:
    detail_type: str
    sequence_no: int
    raw_record: str
    parsed_values: dict[str, Any]
    row_hash: str


@dataclass
class ParsedReservation:
    property_code: str
    snapshot_name: str
    snapshot_date: date
    business_date: date | None
    resort: str | None
    currency_code: str | None
    integration_id: str | None
    arrival_date: date | None
    status: str | None
    reservation_id: str
    details_raw: str
    details_json: dict[str, Any]
    daily_details: list[ParsedDailyDetail]
    row_hash: str
    metadata: dict[str, Any]


class RoiXmlParserError(RuntimeError):
    pass


class RoiXmlParser:
    header_tags = {
        "RESORT",
        "EXPORT_VERSION",
        "CURRENCY_CODE",
        "INTEGRATION_ID",
        "COUNTRY_CODE",
        "TIMEZONE_REGION",
        "NUMBER_ROOMS",
        "BUSINESS_DATE",
        "ASOF_TIME",
        "NUMERIC_CHARACTERS",
        "DATABASE_TIMEZONE_APPLICATION_PARAMETER",
        "DATABASE_TIMEZONE",
        "SESSION_TIMEZONE",
        "OPERA_VERSION_EPATCHLEVEL",
        "RATE_ROOM_TRX_ENABLED",
        "PACE_ENABLED",
        "DATABASE_COMPONENT_VERSIONS",
        "DEFAULT_TRANSACTION_CODE",
        "DAYS",
    }

    def parse(self, file_path: Path, file_context: RoiFileContext) -> Iterator[ParsedReservation]:
        header: dict[str, str | None] = {}
        root_seen = False
        try:
            context = ET.iterparse(str(file_path), events=("start", "end"))
            for event, elem in context:
                tag = self._strip_namespace(elem.tag)
                if event == "start" and not root_seen:
                    root_seen = True
                    if tag != "ROI_SETUP":
                        raise RoiXmlParserError(f"Invalid ROI XML root: {tag}")

                if event != "end":
                    continue

                if tag in self.header_tags and tag not in header:
                    header[tag] = (elem.text or "").strip() or None
                elif tag == "RESERVATIONS":
                    parsed = self._parse_reservation(elem, header, file_context)
                    if parsed:
                        yield parsed
                    elem.clear()
                    parent = getattr(elem, "getparent", lambda: None)()
                    while parent is not None and elem.getprevious() is not None:  # lxml memory cleanup
                        del parent[0]
        except RoiXmlParserError:
            raise
        except Exception as exc:
            raise RoiXmlParserError(f"Unreadable ROI XML file {file_path.name}: {exc}") from exc

    def _parse_reservation(self, elem, header: dict[str, str | None], file_context: RoiFileContext) -> ParsedReservation | None:
        warnings: list[str] = []
        property_code = self._child_text(elem, "PROPERTY_CODE") or file_context.property_code
        reservation_id = self._child_text(elem, "RESRVATION_ID")
        if not reservation_id:
            logger.warning("Skipping reservation without RESRVATION_ID in %s", file_context.file_name)
            return None

        resort = header.get("RESORT")
        business_date = parse_iso_date(header.get("BUSINESS_DATE"))
        if property_code and property_code.upper() != file_context.property_code.upper():
            warnings.append(f"Filename property_code {file_context.property_code} differs from XML PROPERTY_CODE {property_code}")
        if resort and resort.upper() != file_context.property_code.upper():
            warnings.append(f"Filename property_code {file_context.property_code} differs from RESORT {resort}")
        if business_date and business_date != file_context.snapshot_date:
            warnings.append(f"Filename snapshot_date {file_context.snapshot_date} differs from BUSINESS_DATE {business_date}")

        details_raw = self._child_text(elem, "DETAILS") or ""
        details_json = parse_pipe_record(self._trim_details(details_raw), RESERVATION_DETAILS_HEADERS) if details_raw else {}
        daily_details = self._parse_daily_details(elem, file_context, reservation_id)

        arrival_date = parse_iso_date(self._child_text(elem, "ARRIVAL_DATE"))
        status = self._child_text(elem, "STATUS")
        row_hash = stable_hash_dict(
            {
                "file_name": file_context.file_name,
                "property_code": file_context.property_code,
                "snapshot_date": file_context.snapshot_date,
                "reservation_id": reservation_id,
                "details_raw": details_raw,
            }
        )
        metadata = {"header": header.copy(), "warnings": warnings}
        return ParsedReservation(
            property_code=property_code,
            snapshot_name=file_context.snapshot_name,
            snapshot_date=file_context.snapshot_date,
            business_date=business_date,
            resort=resort,
            currency_code=header.get("CURRENCY_CODE"),
            integration_id=header.get("INTEGRATION_ID"),
            arrival_date=arrival_date,
            status=status,
            reservation_id=reservation_id,
            details_raw=details_raw,
            details_json=details_json,
            daily_details=daily_details,
            row_hash=row_hash,
            metadata=metadata,
        )

    def _parse_daily_details(self, reservation_elem, file_context: RoiFileContext, reservation_id: str) -> list[ParsedDailyDetail]:
        res_details = self._find_child(reservation_elem, "RES_DETAILS")
        if res_details is None:
            return []

        results: list[ParsedDailyDetail] = []
        for child in list(res_details):
            detail_type = self._strip_namespace(child.tag)
            headers = DAILY_HEADERS.get(detail_type)
            if headers is None:
                continue
            raw = child.text or ""
            try:
                records = parse_compound_records(raw, headers)
            except Exception as exc:
                logger.warning("Malformed daily detail row %s in %s: %s", detail_type, file_context.file_name, exc)
                continue
            for record in records:
                row_hash = stable_hash_dict(
                    {
                        "file_name": file_context.file_name,
                        "reservation_id": reservation_id,
                        "detail_type": detail_type,
                        "sequence_no": record["sequence_no"],
                        "raw_record": record["raw"],
                    }
                )
                results.append(
                    ParsedDailyDetail(
                        detail_type=detail_type,
                        sequence_no=record["sequence_no"],
                        raw_record=record["raw"],
                        parsed_values=record["values"],
                        row_hash=row_hash,
                    )
                )
        return results

    @staticmethod
    def _trim_details(raw: str) -> str:
        value = raw
        while value.endswith("#"):
            value = value[:-1]
        while value.endswith("{"):
            value = value[:-1]
        return value

    def _child_text(self, elem, child_name: str) -> str | None:
        child = self._find_child(elem, child_name)
        if child is None or child.text is None:
            return None
        return child.text.strip()

    def _find_child(self, elem, child_name: str):
        for child in list(elem):
            if self._strip_namespace(child.tag) == child_name:
                return child
        return None

    @staticmethod
    def _strip_namespace(tag: str) -> str:
        return tag.rsplit("}", 1)[-1] if "}" in tag else tag
