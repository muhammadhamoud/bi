from dataclasses import asdict
from datetime import date

from django.core.management.base import BaseCommand, CommandError

from apps.roi_ingestion.services.ingestion_service import RoiDailyIngestionService
from apps.roi_ingestion.utils.dates import dubai_today


class Command(BaseCommand):
    help = "Ingest ROI daily XML snapshot files from SFTP into the ROI staging database."

    def add_arguments(self, parser):
        date_group = parser.add_mutually_exclusive_group()
        date_group.add_argument("--today", action="store_true", help="Use today in Asia/Dubai timezone.")
        date_group.add_argument("--date", dest="target_date", help="Target date in YYYY-MM-DD format.")
        parser.add_argument("--property", dest="property_code", help="Limit processing to one property code.")
        parser.add_argument("--dry-run", action="store_true", help="Show actions without writing changes.")
        parser.add_argument("--batch-size", type=int, default=5000, help="Bulk insert batch size.")
        parser.add_argument("--database", default="roi_staging", help="Staging database alias.")
        parser.add_argument("--force-reload", action="store_true", help="Process files even if FileRecord is loaded.")
        parser.add_argument(
            "--no-older-unloaded",
            action="store_true",
            help="Only process the target date; do not process older unloaded files.",
        )

    def handle(self, *args, **options):
        if options["target_date"]:
            try:
                target_date = date.fromisoformat(options["target_date"])
            except ValueError as exc:
                raise CommandError("--date must be in YYYY-MM-DD format") from exc
        elif options["today"]:
            target_date = dubai_today()
        else:
            target_date = None

        service = RoiDailyIngestionService(
            batch_size=options["batch_size"],
            dry_run=options["dry_run"],
            staging_db_alias=options["database"],
        )
        result = service.run(
            target_date=target_date,
            property_code=options.get("property_code"),
            process_older_unloaded=not options["no_older_unloaded"],
            force_reload=options["force_reload"],
        )
        self.stdout.write(self.style.SUCCESS("ROI daily ingestion complete"))
        for key, value in asdict(result).items():
            self.stdout.write(f"{key}: {value}")
