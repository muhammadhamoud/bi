from django.contrib import admin

from apps.dataops.files.models import (
    ExpectedFileDefinition,
    FileDownloadHistory,
    FileEventLog,
    FileRecord,
    IngestionJob,
    LoadResult,
    SourceSystem,
    ValidationResult,
)


class FileEventLogInline(admin.TabularInline):
    model = FileEventLog
    extra = 0
    autocomplete_fields = ('actor_user',)
    readonly_fields = ('created_at', 'updated_at')


class IngestionJobInline(admin.TabularInline):
    model = IngestionJob
    extra = 0
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SourceSystem)
class SourceSystemAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'connection_type', 'is_active')
    list_filter = ('connection_type', 'is_active')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ExpectedFileDefinition)
class ExpectedFileDefinitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'property', 'source_system', 'file_type', 'frequency', 'expected_by_hour', 'is_active', 'is_critical')
    list_filter = ('frequency', 'is_active', 'is_critical', 'property', 'source_system')
    search_fields = ('name', 'code', 'file_type', 'property__name', 'source_system__name')
    autocomplete_fields = ('property', 'source_system', 'created_by', 'updated_by')


@admin.register(FileRecord)
class FileRecordAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'property', 'source_system', 'status', 'file_type', 'received_at', 'loaded_at', 'size_bytes')
    list_filter = ('status', 'file_type', 'property', 'source_system')
    search_fields = ('file_name', 'source_reference', 'checksum', 'property__name', 'source_system__name')
    autocomplete_fields = ('property', 'source_system', 'expected_definition', 'uploaded_by', 'retrieved_by', 'created_by', 'updated_by')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [IngestionJobInline, FileEventLogInline]


@admin.register(IngestionJob)
class IngestionJobAdmin(admin.ModelAdmin):
    list_display = ('job_reference', 'file_record', 'status', 'destination_table', 'started_at', 'finished_at')
    list_filter = ('status', 'destination_table')
    search_fields = ('job_reference', 'file_record__file_name', 'destination_table', 'error_message')
    autocomplete_fields = ('file_record',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ValidationResult)
class ValidationResultAdmin(admin.ModelAdmin):
    list_display = ('file_record', 'is_valid', 'warning_count', 'error_count', 'created_at')
    list_filter = ('is_valid',)
    search_fields = ('file_record__file_name', 'summary')
    autocomplete_fields = ('file_record',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(LoadResult)
class LoadResultAdmin(admin.ModelAdmin):
    list_display = ('file_record', 'status', 'destination_table', 'row_count', 'inserted_records', 'updated_records', 'rejected_records')
    list_filter = ('status', 'destination_table')
    search_fields = ('file_record__file_name', 'destination_table', 'summary')
    autocomplete_fields = ('file_record',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(FileEventLog)
class FileEventLogAdmin(admin.ModelAdmin):
    list_display = ('file_record', 'event_type', 'actor_type', 'actor_user', 'created_at')
    list_filter = ('event_type', 'actor_type', 'created_at')
    search_fields = ('file_record__file_name', 'event_type', 'message', 'actor_user__email')
    autocomplete_fields = ('file_record', 'actor_user')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(FileDownloadHistory)
class FileDownloadHistoryAdmin(admin.ModelAdmin):
    list_display = ('file_record', 'user', 'property', 'reason', 'source_workflow', 'created_at')
    list_filter = ('property', 'source_workflow', 'created_at')
    search_fields = ('file_record__file_name', 'user__email', 'property__name', 'reason', 'source_workflow')
    autocomplete_fields = ('file_record', 'user', 'property')
    readonly_fields = ('created_at', 'updated_at')
