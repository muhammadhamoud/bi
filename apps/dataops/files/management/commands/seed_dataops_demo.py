from datetime import timedelta
import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.dataops.files.models import ExpectedFileDefinition, FileDownloadHistory, FileEventLog, FileRecord, IngestionJob, LoadResult, SourceSystem, ValidationResult
from apps.properties.core.models import Property

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed demo file lifecycle and ingestion data.'

    def handle(self, *args, **options):
        random.seed(7)
        users = list(User.objects.all())
        properties = list(Property.objects.filter(is_active=True))
        if not properties:
            self.stdout.write(self.style.WARNING('No properties found. Run seed_properties first.'))
            return

        source_system, _ = SourceSystem.objects.get_or_create(code='OPERA', defaults={'name': 'Oracle Opera PMS', 'slug': 'oracle-opera-pms', 'description': 'Demo PMS source', 'connection_type': 'sftp'})
        pickup_source, _ = SourceSystem.objects.get_or_create(code='PICKUP', defaults={'name': 'Pickup Feed', 'slug': 'pickup-feed', 'description': 'Daily pickup source', 'connection_type': 'api'})

        today = timezone.localdate()
        for property_obj in properties:
            expected_defs = [
                ('ROOM_REV', 'Room revenue file', 'csv', source_system),
                ('PICKUP', 'Daily pickup file', 'csv', pickup_source),
            ]
            for code, name, file_type, source in expected_defs:
                definition, _ = ExpectedFileDefinition.objects.get_or_create(
                    property=property_obj,
                    source_system=source,
                    code=code,
                    defaults={'name': name, 'file_type': file_type, 'destination_table': f'stg_{code.lower()}', 'is_critical': True if code == 'ROOM_REV' else False},
                )
                for offset in range(4):
                    expected_date = today - timedelta(days=offset)
                    status = random.choice([
                        FileRecord.LifecycleStatus.MISSING,
                        FileRecord.LifecycleStatus.RECEIVED,
                        FileRecord.LifecycleStatus.LOADED,
                        FileRecord.LifecycleStatus.FAILED,
                    ])
                    file_record, _ = FileRecord.objects.get_or_create(
                        property=property_obj,
                        source_system=source,
                        expected_definition=definition,
                        file_name=f'{property_obj.code}_{code}_{expected_date.isoformat()}',
                        expected_for_date=expected_date,
                        defaults={
                            'file_type': file_type,
                            'status': status,
                            'size_bytes': random.randint(5000, 950000),
                            'received_at': timezone.now() - timedelta(hours=random.randint(1, 8)) if status != FileRecord.LifecycleStatus.MISSING else None,
                            'loaded_at': timezone.now() if status == FileRecord.LifecycleStatus.LOADED else None,
                            'failed_at': timezone.now() if status == FileRecord.LifecycleStatus.FAILED else None,
                            'notes': 'Demo lifecycle item',
                        },
                    )
                    FileEventLog.objects.get_or_create(
                        file_record=file_record,
                        event_type='status_transition',
                        status_to=file_record.status,
                        defaults={'message': f'File entered {file_record.status} state', 'actor_type': 'system'},
                    )
                    if file_record.status in [FileRecord.LifecycleStatus.RECEIVED, FileRecord.LifecycleStatus.LOADED, FileRecord.LifecycleStatus.FAILED]:
                        ValidationResult.objects.get_or_create(
                            file_record=file_record,
                            defaults={
                                'is_valid': file_record.status != FileRecord.LifecycleStatus.FAILED,
                                'warning_count': 1 if file_record.status == FileRecord.LifecycleStatus.RECEIVED else 0,
                                'error_count': 1 if file_record.status == FileRecord.LifecycleStatus.FAILED else 0,
                                'summary': 'Basic schema checks completed.',
                            },
                        )
                        IngestionJob.objects.get_or_create(
                            file_record=file_record,
                            job_reference=f'ING-{property_obj.code}-{expected_date:%Y%m%d}',
                            defaults={
                                'status': IngestionJob.Status.SUCCESS if file_record.status == FileRecord.LifecycleStatus.LOADED else IngestionJob.Status.FAILED if file_record.status == FileRecord.LifecycleStatus.FAILED else IngestionJob.Status.RUNNING,
                                'destination_table': definition.destination_table,
                                'processing_duration_seconds': random.randint(12, 180),
                                'transformation_summary': 'Parsed, normalized, and matched lookup dimensions.',
                                'error_message': 'Demo validation mismatch' if file_record.status == FileRecord.LifecycleStatus.FAILED else '',
                            },
                        )
                    if file_record.status == FileRecord.LifecycleStatus.LOADED:
                        LoadResult.objects.get_or_create(
                            file_record=file_record,
                            defaults={
                                'destination_table': definition.destination_table,
                                'row_count': random.randint(40, 400),
                                'inserted_records': random.randint(35, 390),
                                'updated_records': random.randint(0, 30),
                                'rejected_records': random.randint(0, 5),
                                'duplicate_records': random.randint(0, 4),
                                'summary': 'Load completed with standard dimensional enrichment.',
                            },
                        )
                        if users:
                            FileDownloadHistory.objects.get_or_create(
                                file_record=file_record,
                                user=users[0],
                                property=property_obj,
                                defaults={'reason': 'Daily review', 'source_workflow': 'dashboard'},
                            )
        self.stdout.write(self.style.SUCCESS('DataOps demo data seeded.'))
