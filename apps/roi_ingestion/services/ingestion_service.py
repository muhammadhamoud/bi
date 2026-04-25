from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
import logging
from pathlib import Path
from typing import Any

from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from django.core.exceptions import ImproperlyConfigured


from apps.roi_ingestion.services.file_discovery import RoiFileDescriptor, RoiFileDiscoveryService
from apps.roi_ingestion.services.missing_detector import MissingFileDetector
from apps.roi_ingestion.services.model_resolver import get_file_record_model, get_property_model, get_source_system_model
from apps.roi_ingestion.services.roi_xml_parser import RoiFileContext, RoiXmlParser, RoiXmlParserError
from apps.roi_ingestion.services.sftp_client import RoiSftpClient
from apps.roi_ingestion.services.staging_loader import RoiStagingLoader
from apps.roi_ingestion.utils.dates import dubai_today
from apps.roi_ingestion.utils.hashing import sha256_file

logger = logging.getLogger(__name__)


@dataclass
class RoiIngestionResult:
    files_found: int = 0
    files_missing: int = 0
    files_skipped: int = 0
    files_processed: int = 0
    files_failed: int = 0
    reservations_inserted: int = 0
    detail_rows_inserted: int = 0
    errors: list[str] = field(default_factory=list)


class RoiDailyIngestionService:
    def __init__(
        self,
        *,
        source_system_code: str = "ROI_DAILY",
        batch_size: int = 5000,
        dry_run: bool = False,
        staging_db_alias: str = "roi_staging",
        sftp_client: RoiSftpClient | None = None,
    ):
        self.source_system_code = source_system_code
        self.batch_size = batch_size
        self.dry_run = dry_run
        self.staging_db_alias = staging_db_alias
        self.sftp_client = sftp_client
        self.discovery = RoiFileDiscoveryService()
        self.missing_detector = MissingFileDetector()
        self.parser = RoiXmlParser()
        self.loader = RoiStagingLoader(batch_size=batch_size, using=staging_db_alias)

    def run(
        self,
        *,
        target_date: date | None = None,
        property_code: str | None = None,
        process_older_unloaded: bool = True,
        force_reload: bool = False,
    ) -> RoiIngestionResult:
        result = RoiIngestionResult()
        target_date = target_date or dubai_today()
        source_system = self._get_source_system()
        active_properties = self._get_active_properties(property_code=property_code)
        property_by_code = {str(prop.code).upper(): prop for prop in active_properties}

        client_context = self.sftp_client or RoiSftpClient()
        with client_context as sftp:
            remote_files = sftp.list_files()
            file_sizes = sftp.list_file_sizes(remote_files)
            discovery = self.discovery.discover(
                remote_files,
                file_sizes=file_sizes,
                property_code=property_code,
                target_date=target_date,
                process_older_unloaded=process_older_unloaded,
            )
            result.files_found = len(discovery.valid_files)

            missing = self.missing_detector.detect(
                active_properties=active_properties,
                target_date=target_date,
                available_file_names={item.file_name for item in discovery.valid_files},
            )
            result.files_missing = len(missing)
            self._mark_missing_files(missing, source_system, result)

            file_records = self._get_file_records(source_system, active_properties, discovery.valid_files)
            for descriptor in discovery.valid_files:
                property_obj = property_by_code.get(descriptor.property_code)
                if property_obj is None:
                    result.files_skipped += 1
                    logger.warning("Skipping ROI file for inactive/unknown property: %s", descriptor.file_name)
                    continue

                file_record = self._get_or_create_file_record(
                    source_system=source_system,
                    property_obj=property_obj,
                    descriptor=descriptor,
                    existing=file_records,
                )
                if not force_reload and self._status_is(file_record, "LOADED", "loaded"):
                    result.files_skipped += 1
                    continue
                if self.dry_run:
                    result.files_skipped += 1
                    continue

                try:
                    self._process_file(
                        sftp=sftp,
                        descriptor=descriptor,
                        file_record=file_record,
                        property_obj=property_obj,
                        result=result,
                    )
                except Exception as exc:
                    logger.exception("ROI ingestion failed for %s", descriptor.file_name)
                    result.files_failed += 1
                    result.errors.append(f"{descriptor.file_name}: {exc}")
                    self._mark_failed(file_record, exc)
        return result

    def _process_file(self, *, sftp, descriptor: RoiFileDescriptor, file_record, property_obj, result: RoiIngestionResult) -> None:
        self._update_status(file_record, "RECEIVED", received_at=timezone.now(), size_bytes=descriptor.size_bytes or 0)
        local_dir = Path(getattr(settings, "ROI_LOCAL_DOWNLOAD_DIR", Path("var/roi_downloads")))
        local_path = sftp.download_file(descriptor.file_name, local_dir)
        checksum = sha256_file(local_path)
        self._update_status(
            file_record,
            "DOWNLOADED",
            checksum=checksum,
            size_bytes=local_path.stat().st_size,
            storage_path=str(local_path),
        )
        self._update_status(file_record, "PROCESSING", processing_started_at=timezone.now())

        context = RoiFileContext(
            file_name=descriptor.file_name,
            snapshot_name=descriptor.snapshot_name,
            property_code=descriptor.property_code,
            snapshot_date=descriptor.snapshot_date,
            file_type=descriptor.file_type,
        )
        parsed_iter = self.parser.parse(local_path, context)
        self._update_status(file_record, "VALIDATED", validated_at=timezone.now())
        reservation_count, detail_count = self.loader.load_file(
            file_record=file_record,
            property_obj=property_obj,
            source_system_code=self.source_system_code,
            parsed_reservations=parsed_iter,
        )
        result.reservations_inserted += reservation_count
        result.detail_rows_inserted += detail_count
        result.files_processed += 1
        self._update_status(file_record, "LOADED", loaded_at=timezone.now())

    # def _get_source_system(self):
    #     SourceSystem = get_source_system_model()
    #     return SourceSystem.objects.using("default").filter(Q(code=self.source_system_code) | Q(name=self.source_system_code)).first()

    def _get_source_system(self):
        SourceSystem = get_source_system_model()

        value = self.source_system_code
        slug_value = value.lower().replace("_", "-")

        field_names = {field.name for field in SourceSystem._meta.fields}

        query = Q()

        if "code" in field_names:
            query |= Q(code__iexact=value)

        if "slug" in field_names:
            query |= Q(slug__iexact=value)
            query |= Q(slug__iexact=slug_value)

        if "name" in field_names:
            query |= Q(name__iexact=value)
            query |= Q(name__iexact=value.replace("_", " "))

        if not query:
            raise ImproperlyConfigured(
                f"{SourceSystem.__name__} must have at least one of these fields: "
                f"code, slug, or name."
            )

        source_system = (
            SourceSystem.objects.using("default")
            .filter(query)
            .first()
        )

        if not source_system:
            raise ImproperlyConfigured(
                f"Could not find SourceSystem for {value!r}. "
                f"Create one in the default database with slug/name matching "
                f"{value!r} or {slug_value!r}."
            )

        return source_system

    def _get_active_properties(self, *, property_code: str | None) -> list[Any]:
        Property = get_property_model()
        qs = Property.objects.using("default").filter(is_active=True)
        if property_code:
            qs = qs.filter(code__iexact=property_code)
        return list(qs)

    def _get_file_records(self, source_system, active_properties: list[Any], descriptors: list[RoiFileDescriptor]) -> dict[tuple[int, int, str], Any]:
        if not source_system or not descriptors:
            return {}
        FileRecord = get_file_record_model()
        property_ids = [prop.id for prop in active_properties]
        file_names = [item.file_name for item in descriptors]
        rows = FileRecord.objects.using("default").filter(
            source_system=source_system,
            property_id__in=property_ids,
            file_name__in=file_names,
        )
        return {(row.source_system_id, row.property_id, row.file_name): row for row in rows}

    def _get_or_create_file_record(self, *, source_system, property_obj, descriptor: RoiFileDescriptor, existing: dict):
        FileRecord = get_file_record_model()
        key = (source_system.id, property_obj.id, descriptor.file_name)
        file_record = existing.get(key)
        if file_record:
            return file_record
        file_record, _ = FileRecord.objects.using("default").get_or_create(
            source_system=source_system,
            property=property_obj,
            file_name=descriptor.file_name,
            defaults={
                "file_type": descriptor.file_type,
                "status": self._status_value(FileRecord, "RECEIVED", "received"),
                "expected_for_date": descriptor.snapshot_date,
                "source_reference": descriptor.snapshot_name,
                "size_bytes": descriptor.size_bytes or 0,
                "received_at": timezone.now(),
                "metadata": {"snapshot_name": descriptor.snapshot_name, "property_code": descriptor.property_code},
            },
        )
        existing[key] = file_record
        return file_record

    def _mark_missing_files(self, missing, source_system, result: RoiIngestionResult) -> None:
        if self.dry_run or not source_system:
            return
        FileRecord = get_file_record_model()
        for expected in missing:
            FileRecord.objects.using("default").update_or_create(
                source_system=source_system,
                property=expected.property_obj,
                file_name=expected.file_name,
                defaults={
                    "file_type": "XML",
                    "status": self._status_value(FileRecord, "MISSING", "missing"),
                    "expected_for_date": expected.expected_date,
                    "source_reference": "ROI_DAILY",
                    "metadata": {"property_code": expected.property_code, "expected": True},
                },
            )

    def _mark_failed(self, file_record, exc: Exception) -> None:
        metadata = dict(getattr(file_record, "metadata", {}) or {})
        metadata["error"] = {"type": exc.__class__.__name__, "message": str(exc)[:1000]}
        self._update_status(
            file_record,
            "FAILED",
            failed_at=timezone.now(),
            notes=str(exc)[:1000],
            metadata=metadata,
        )

    def _update_status(self, file_record, status_name: str, **fields) -> None:
        FileRecord = get_file_record_model()
        file_record.status = self._status_value(FileRecord, status_name, status_name.lower())
        update_fields = ["status"]
        for name, value in fields.items():
            setattr(file_record, name, value)
            update_fields.append(name)
        file_record.save(using="default", update_fields=update_fields)

    @staticmethod
    def _status_value(FileRecord, status_name: str, fallback: str) -> str:
        lifecycle = getattr(FileRecord, "LifecycleStatus", None)
        if lifecycle and hasattr(lifecycle, status_name):
            return getattr(lifecycle, status_name)
        return fallback

    def _status_is(self, file_record, status_name: str, fallback: str) -> bool:
        FileRecord = get_file_record_model()
        return file_record.status == self._status_value(FileRecord, status_name, fallback)
