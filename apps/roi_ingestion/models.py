from django.db import models


class RoiReservationStage(models.Model):
    id = models.BigAutoField(primary_key=True)
    file_record_id = models.BigIntegerField(db_index=True)
    property_id = models.BigIntegerField(db_index=True)
    source_system_code = models.CharField(max_length=60)
    file_name = models.CharField(max_length=255)
    property_code = models.CharField(max_length=40)
    snapshot_name = models.CharField(max_length=80)
    snapshot_date = models.DateField(db_index=True)
    business_date = models.DateField(null=True, blank=True, db_index=True)
    resort = models.CharField(max_length=40, null=True, blank=True)
    currency_code = models.CharField(max_length=10, null=True, blank=True)
    integration_id = models.CharField(max_length=80, null=True, blank=True)
    arrival_date = models.DateField(null=True, blank=True, db_index=True)
    status = models.CharField(max_length=80, null=True, blank=True)
    reservation_id = models.CharField(max_length=120, db_index=True)
    details_raw = models.TextField(blank=True)
    details_json = models.JSONField(default=dict, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    row_hash = models.CharField(max_length=64, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "roi_reservation_stage"
        constraints = [
            models.UniqueConstraint(
                fields=["file_record_id", "reservation_id"],
                name="uniq_roi_reservation_stage_file_reservation",
            )
        ]
        indexes = [
            models.Index(fields=["file_record_id"], name="roi_res_file_idx"),
            models.Index(fields=["property_id"], name="roi_res_property_idx"),
            models.Index(fields=["snapshot_date"], name="roi_res_snapshot_idx"),
            models.Index(fields=["business_date"], name="roi_res_business_idx"),
            models.Index(fields=["reservation_id"], name="roi_res_reservation_idx"),
            models.Index(fields=["row_hash"], name="roi_res_hash_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.file_name} / {self.reservation_id}"


class RoiReservationDailyStage(models.Model):
    id = models.BigAutoField(primary_key=True)
    file_record_id = models.BigIntegerField(db_index=True)
    property_id = models.BigIntegerField(db_index=True)
    reservation_stage_id = models.BigIntegerField(null=True, blank=True, db_index=True)
    reservation_row_hash = models.CharField(max_length=64, db_index=True)
    source_system_code = models.CharField(max_length=60)
    file_name = models.CharField(max_length=255)
    property_code = models.CharField(max_length=40)
    snapshot_date = models.DateField(db_index=True)
    reservation_id = models.CharField(max_length=120, db_index=True)
    detail_type = models.CharField(max_length=80, db_index=True)
    sequence_no = models.IntegerField()
    raw_record = models.TextField(blank=True)
    parsed_values = models.JSONField(default=dict, blank=True)
    row_hash = models.CharField(max_length=64, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "roi_reservation_daily_stage"
        constraints = [
            models.UniqueConstraint(
                fields=["file_record_id", "reservation_id", "detail_type", "sequence_no", "row_hash"],
                name="uniq_roi_daily_stage_file_res_detail_seq_hash",
            )
        ]
        indexes = [
            models.Index(fields=["file_record_id"], name="roi_daily_file_idx"),
            models.Index(fields=["property_id"], name="roi_daily_property_idx"),
            models.Index(fields=["snapshot_date"], name="roi_daily_snapshot_idx"),
            models.Index(fields=["reservation_id"], name="roi_daily_reservation_idx"),
            models.Index(fields=["detail_type"], name="roi_daily_type_idx"),
            models.Index(fields=["row_hash"], name="roi_daily_hash_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.file_name} / {self.reservation_id} / {self.detail_type}"
