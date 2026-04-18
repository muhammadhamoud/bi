from django.conf import settings
from django.db import models

from apps.core.common.models import ActivatableModel, AuditUserModel, NamedSlugModel, SortableModel, TimeStampedModel


class SourceSystem(NamedSlugModel):
    connection_type = models.CharField(max_length=60, blank=True)

    class Meta:
        db_table = 'dataops_source_systems'
        ordering = ['name']




class ExpectedFileDefinition(TimeStampedModel, ActivatableModel, AuditUserModel):
    class Frequency(models.TextChoices):
        DAILY = 'daily', 'Daily'
        WEEKLY = 'weekly', 'Weekly'
        MONTHLY = 'monthly', 'Monthly'

    property = models.ForeignKey('propertycore.Property', on_delete=models.CASCADE, related_name='expected_file_definitions')
    source_system = models.ForeignKey(SourceSystem, on_delete=models.CASCADE, related_name='expected_file_definitions')
    code = models.CharField(max_length=60)
    name = models.CharField(max_length=140)
    file_type = models.CharField(max_length=60)
    expected_pattern = models.CharField(max_length=140, blank=True)
    frequency = models.CharField(max_length=20, choices=Frequency.choices, default=Frequency.DAILY)
    destination_table = models.CharField(max_length=120, blank=True)
    expected_by_hour = models.PositiveSmallIntegerField(default=8)
    is_critical = models.BooleanField(default=False)

    class Meta:
        db_table = 'dataops_expected_file_definitions'
        unique_together = ('property', 'source_system', 'code')
        ordering = ['property__name', 'name']

    def __str__(self):
        return self.name


class FileRecord(TimeStampedModel, ActivatableModel, AuditUserModel):
    class LifecycleStatus(models.TextChoices):
        EXPECTED = 'expected', 'Expected'
        MISSING = 'missing', 'Missing'
        RECEIVED = 'received', 'Received'
        VALIDATED = 'validated', 'Validated'
        PROCESSING = 'processing', 'Processing'
        LOADED = 'loaded', 'Loaded to database'
        FAILED = 'failed', 'Failed'
        ARCHIVED = 'archived', 'Archived'
        DOWNLOADED = 'downloaded', 'Downloaded'

    property = models.ForeignKey('propertycore.Property', on_delete=models.CASCADE, related_name='file_records')
    source_system = models.ForeignKey(SourceSystem, on_delete=models.CASCADE, related_name='file_records')
    expected_definition = models.ForeignKey(ExpectedFileDefinition, on_delete=models.SET_NULL, null=True, blank=True, related_name='file_records')
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=60)
    status = models.CharField(max_length=30, choices=LifecycleStatus.choices, default=LifecycleStatus.EXPECTED, db_index=True)
    expected_for_date = models.DateField(null=True, blank=True)
    source_reference = models.CharField(max_length=120, blank=True)
    checksum = models.CharField(max_length=140, blank=True)
    size_bytes = models.PositiveBigIntegerField(default=0)
    storage_path = models.CharField(max_length=255, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_files')
    retrieved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='retrieved_files')
    received_at = models.DateTimeField(null=True, blank=True)
    validated_at = models.DateTimeField(null=True, blank=True)
    processing_started_at = models.DateTimeField(null=True, blank=True)
    loaded_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    archived_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'dataops_file_records'
        ordering = ['-created_at']
        permissions = [('download_filerecord', 'Can download file content and metadata')]

    def __str__(self):
        return self.file_name


class IngestionJob(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        RUNNING = 'running', 'Running'
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed'

    file_record = models.ForeignKey(FileRecord, on_delete=models.CASCADE, related_name='ingestion_jobs')
    job_reference = models.CharField(max_length=80)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    destination_table = models.CharField(max_length=120, blank=True)
    processing_duration_seconds = models.PositiveIntegerField(default=0)
    transformation_summary = models.TextField(blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        db_table = 'dataops_ingestion_jobs'
        ordering = ['-created_at']


class ValidationResult(TimeStampedModel):
    file_record = models.OneToOneField(FileRecord, on_delete=models.CASCADE, related_name='validation_result')
    is_valid = models.BooleanField(default=False)
    warning_count = models.PositiveIntegerField(default=0)
    error_count = models.PositiveIntegerField(default=0)
    summary = models.TextField(blank=True)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'dataops_validation_results'


class LoadResult(TimeStampedModel):
    class Status(models.TextChoices):
        SUCCESS = 'success', 'Success'
        PARTIAL = 'partial', 'Partial'
        FAILED = 'failed', 'Failed'

    file_record = models.OneToOneField(FileRecord, on_delete=models.CASCADE, related_name='load_result')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUCCESS)
    destination_table = models.CharField(max_length=120)
    row_count = models.PositiveIntegerField(default=0)
    inserted_records = models.PositiveIntegerField(default=0)
    updated_records = models.PositiveIntegerField(default=0)
    rejected_records = models.PositiveIntegerField(default=0)
    duplicate_records = models.PositiveIntegerField(default=0)
    summary = models.TextField(blank=True)

    class Meta:
        db_table = 'dataops_load_results'


class FileEventLog(TimeStampedModel):
    file_record = models.ForeignKey(FileRecord, on_delete=models.CASCADE, related_name='event_logs')
    event_type = models.CharField(max_length=80)
    status_from = models.CharField(max_length=30, blank=True)
    status_to = models.CharField(max_length=30, blank=True)
    message = models.TextField(blank=True)
    actor_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    actor_type = models.CharField(max_length=20, default='system')
    payload = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'dataops_file_event_logs'
        ordering = ['created_at']


class FileDownloadHistory(TimeStampedModel):
    file_record = models.ForeignKey(FileRecord, on_delete=models.CASCADE, related_name='download_history')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    property = models.ForeignKey('propertycore.Property', on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.CharField(max_length=255, blank=True)
    source_workflow = models.CharField(max_length=120, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = 'dataops_file_download_history'
        ordering = ['-created_at']
