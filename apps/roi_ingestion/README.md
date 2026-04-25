# ROI Daily XML Ingestion Django App

This package implements a production-ready, reusable Django ingestion system for ROI daily XML snapshot files stored on SFTP.

## Proposed database constraints

### Operational/default database
`FileRecord`, `Property`, `SourceSystem`, and `ExpectedFileDefinition` remain in the default application database. The recommended operational uniqueness constraint is:

```python
models.UniqueConstraint(
    fields=["source_system", "property", "file_name"],
    name="uniq_file_record_source_property_file_name",
)
```

This lets the ingestion service safely create or update the same expected/missing/received file row without duplicates, including the case where a previously missing file later arrives.

### ROI staging database
The parsed ROI rows are stored in `roi_staging` only. Cross-database foreign keys are intentionally avoided. Staging models store plain IDs and denormalized references:

- `file_record_id`
- `property_id`
- `source_system_code`
- `file_name`
- `property_code`
- `snapshot_name`
- `snapshot_date`

Staging idempotency constraints:

```python
UniqueConstraint(
    fields=["file_record_id", "reservation_id"],
    name="uniq_roi_reservation_stage_file_reservation",
)

UniqueConstraint(
    fields=["file_record_id", "reservation_id", "detail_type", "sequence_no", "row_hash"],
    name="uniq_roi_daily_stage_file_res_detail_seq_hash",
)
```

The loader also uses `bulk_create(..., ignore_conflicts=True)` so re-runs do not duplicate rows.

## Ingestion flow

1. Resolve `target_date`; default is today in `Asia/Dubai`.
2. Fetch the `SourceSystem` from the default DB.
3. Fetch active properties from the default DB in one query.
4. List remote SFTP files.
5. Parse valid ROI filenames and log/skip invalid filenames.
6. Detect expected files missing for the target date.
7. Create/update `FileRecord` rows in the default DB.
8. Skip files already `loaded` unless `force_reload=True`.
9. Download the remote file locally.
10. Calculate SHA-256 checksum and file size.
11. Mark lifecycle statuses: `received`, `downloaded`, `processing`, `validated`, `loaded`, or `failed`.
12. Stream parse XML reservation-by-reservation.
13. Batch insert reservations and daily detail rows into `roi_staging` using `.using("roi_staging")`.
14. Return `RoiIngestionResult` counts and errors.

Default DB status updates and `roi_staging` inserts are not wrapped in one cross-database transaction. This keeps the system recoverable across databases.

## Installation

Copy `roi_ingestion/` into your Django project and add it to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "roi_ingestion",
]
```

Add the router:

```python
DATABASE_ROUTERS = [
    "apps.roi_ingestion.db_router.RoiStagingRouter",
]
```

Configure database aliases:

```python
DATABASES = {
    "default": {...},
    "roi_staging": {...},
}
```

Configure existing model paths if your project uses different app labels:

```python
ROI_FILE_RECORD_MODEL = "files.FileRecord"
ROI_PROPERTY_MODEL = "propertycore.Property"
ROI_SOURCE_SYSTEM_MODEL = "integrations.SourceSystem"
ROI_EXPECTED_FILE_DEFINITION_MODEL = "files.ExpectedFileDefinition"  # optional
```

Configure SFTP:

```python
SFTP_HOST = "sftp.example.com"
SFTP_PORT = 22
SFTP_USERNAME = "roi_user"
SFTP_PASSWORD = "..."              # optional
SFTP_PRIVATE_KEY = "/path/key.pem" # optional
SFTP_REMOTE_DIR = "/outbound/roi"
SFTP_ARCHIVE_DIR = "/archive/roi"  # optional
ROI_LOCAL_DOWNLOAD_DIR = BASE_DIR / "var" / "roi_downloads"
```

Do not log or commit SFTP credentials.

## Migrations

Create the staging models only in `roi_staging`:

```bash
python manage.py migrate roi_ingestion --database=roi_staging
```

The router prevents these staging models from migrating into `default` and prevents non-staging operational models from moving into `roi_staging`.

## Management command

```bash
python manage.py ingest_roi_daily --today
python manage.py ingest_roi_daily --date 2026-04-22
python manage.py ingest_roi_daily --property DXBJV
python manage.py ingest_roi_daily --dry-run
python manage.py ingest_roi_daily --batch-size 5000
python manage.py ingest_roi_daily --database roi_staging
python manage.py ingest_roi_daily --force-reload
```

## Celery task

```python
from apps.roi_ingestion.tasks import ingest_roi_daily_task

ingest_roi_daily_task.delay(target_date="2026-04-22", property_code="DXBJV")
```

Example Celery Beat configuration is included in `roi_ingestion/tasks.py`.

## Notes for integration

- The service assumes `Property` has a `code` field and an `is_active` field.
- The service assumes `SourceSystem` can be found by `code` or `name` equal to `source_system_code`.
- If your project differs, adjust `model_resolver.py` or the small query helpers in `ingestion_service.py`.
- Core ingestion logic is only in services. The management command and Celery task only instantiate and call `RoiDailyIngestionService`.
