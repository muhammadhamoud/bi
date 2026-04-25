from __future__ import annotations

from collections.abc import Iterable
from django.db import transaction

from apps.roi_ingestion.models import RoiReservationDailyStage, RoiReservationStage
from apps.roi_ingestion.services.roi_xml_parser import ParsedReservation


class RoiStagingLoader:
    def __init__(self, batch_size: int = 5000, using: str = "roi_staging"):
        self.batch_size = batch_size
        self.using = using

    def load_file(
        self,
        *,
        file_record,
        property_obj,
        source_system_code: str,
        parsed_reservations: Iterable[ParsedReservation],
    ) -> tuple[int, int]:
        reservation_batch: list[RoiReservationStage] = []
        detail_batch: list[RoiReservationDailyStage] = []
        reservation_count = 0
        detail_count = 0

        for parsed in parsed_reservations:
            reservation_batch.append(
                RoiReservationStage(
                    file_record_id=file_record.id,
                    property_id=property_obj.id,
                    source_system_code=source_system_code,
                    file_name=file_record.file_name,
                    property_code=parsed.property_code,
                    snapshot_name=parsed.snapshot_name,
                    snapshot_date=parsed.snapshot_date,
                    business_date=parsed.business_date,
                    resort=parsed.resort,
                    currency_code=parsed.currency_code,
                    integration_id=parsed.integration_id,
                    arrival_date=parsed.arrival_date,
                    status=parsed.status,
                    reservation_id=parsed.reservation_id,
                    details_raw=parsed.details_raw,
                    details_json=parsed.details_json,
                    metadata=parsed.metadata,
                    row_hash=parsed.row_hash,
                )
            )
            reservation_count += 1

            for detail in parsed.daily_details:
                detail_batch.append(
                    RoiReservationDailyStage(
                        file_record_id=file_record.id,
                        property_id=property_obj.id,
                        reservation_stage_id=None,
                        reservation_row_hash=parsed.row_hash,
                        source_system_code=source_system_code,
                        file_name=file_record.file_name,
                        property_code=parsed.property_code,
                        snapshot_date=parsed.snapshot_date,
                        reservation_id=parsed.reservation_id,
                        detail_type=detail.detail_type,
                        sequence_no=detail.sequence_no,
                        raw_record=detail.raw_record,
                        parsed_values=detail.parsed_values,
                        row_hash=detail.row_hash,
                    )
                )
                detail_count += 1

            if len(reservation_batch) >= self.batch_size:
                self._flush_reservations(reservation_batch)
                reservation_batch.clear()
            if len(detail_batch) >= self.batch_size:
                self._flush_details(detail_batch)
                detail_batch.clear()

        if reservation_batch:
            self._flush_reservations(reservation_batch)
        if detail_batch:
            self._flush_details(detail_batch)
        return reservation_count, detail_count

    def _flush_reservations(self, batch: list[RoiReservationStage]) -> None:
        with transaction.atomic(using=self.using):
            RoiReservationStage.objects.using(self.using).bulk_create(
                batch,
                batch_size=self.batch_size,
                ignore_conflicts=True,
            )

    def _flush_details(self, batch: list[RoiReservationDailyStage]) -> None:
        with transaction.atomic(using=self.using):
            RoiReservationDailyStage.objects.using(self.using).bulk_create(
                batch,
                batch_size=self.batch_size,
                ignore_conflicts=True,
            )
