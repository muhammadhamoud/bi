# Generated example migration for ROI staging models.
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="RoiReservationStage",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("file_record_id", models.BigIntegerField(db_index=True)),
                ("property_id", models.BigIntegerField(db_index=True)),
                ("source_system_code", models.CharField(max_length=60)),
                ("file_name", models.CharField(max_length=255)),
                ("property_code", models.CharField(max_length=40)),
                ("snapshot_name", models.CharField(max_length=80)),
                ("snapshot_date", models.DateField(db_index=True)),
                ("business_date", models.DateField(blank=True, db_index=True, null=True)),
                ("resort", models.CharField(blank=True, max_length=40, null=True)),
                ("currency_code", models.CharField(blank=True, max_length=10, null=True)),
                ("integration_id", models.CharField(blank=True, max_length=80, null=True)),
                ("arrival_date", models.DateField(blank=True, db_index=True, null=True)),
                ("status", models.CharField(blank=True, max_length=80, null=True)),
                ("reservation_id", models.CharField(db_index=True, max_length=120)),
                ("details_raw", models.TextField(blank=True)),
                ("details_json", models.JSONField(blank=True, default=dict)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("row_hash", models.CharField(db_index=True, max_length=64)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"db_table": "roi_reservation_stage"},
        ),
        migrations.CreateModel(
            name="RoiReservationDailyStage",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("file_record_id", models.BigIntegerField(db_index=True)),
                ("property_id", models.BigIntegerField(db_index=True)),
                ("reservation_stage_id", models.BigIntegerField(blank=True, db_index=True, null=True)),
                ("reservation_row_hash", models.CharField(db_index=True, max_length=64)),
                ("source_system_code", models.CharField(max_length=60)),
                ("file_name", models.CharField(max_length=255)),
                ("property_code", models.CharField(max_length=40)),
                ("snapshot_date", models.DateField(db_index=True)),
                ("reservation_id", models.CharField(db_index=True, max_length=120)),
                ("detail_type", models.CharField(db_index=True, max_length=80)),
                ("sequence_no", models.IntegerField()),
                ("raw_record", models.TextField(blank=True)),
                ("parsed_values", models.JSONField(blank=True, default=dict)),
                ("row_hash", models.CharField(db_index=True, max_length=64)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"db_table": "roi_reservation_daily_stage"},
        ),
        migrations.AddConstraint(
            model_name="roireservationstage",
            constraint=models.UniqueConstraint(fields=("file_record_id", "reservation_id"), name="uniq_roi_reservation_stage_file_reservation"),
        ),
        migrations.AddConstraint(
            model_name="roireservationdailystage",
            constraint=models.UniqueConstraint(fields=("file_record_id", "reservation_id", "detail_type", "sequence_no", "row_hash"), name="uniq_roi_daily_stage_file_res_detail_seq_hash"),
        ),
    ]
