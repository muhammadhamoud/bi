import csv
from io import StringIO

from django.http import HttpResponse
from django.utils import timezone

from apps.dataops.files.models import FileRecord
from apps.dataops.files.selectors import accessible_event_logs, accessible_file_records


def build_dataops_dashboard(user):
    queryset = accessible_file_records(user)
    today = timezone.localdate()
    return {
        'stats': {
            'expected_files': queryset.filter(status__in=[FileRecord.LifecycleStatus.EXPECTED, FileRecord.LifecycleStatus.MISSING]).count(),
            'missing_files': queryset.filter(status=FileRecord.LifecycleStatus.MISSING).count(),
            'received_files': queryset.filter(status__in=[FileRecord.LifecycleStatus.RECEIVED, FileRecord.LifecycleStatus.VALIDATED, FileRecord.LifecycleStatus.PROCESSING]).count(),
            'failed_files': queryset.filter(status=FileRecord.LifecycleStatus.FAILED).count(),
            'loaded_files': queryset.filter(status=FileRecord.LifecycleStatus.LOADED).count(),
            'pending_validation': queryset.filter(status=FileRecord.LifecycleStatus.RECEIVED).count(),
            'overdue_files': queryset.filter(status=FileRecord.LifecycleStatus.MISSING, expected_for_date__lt=today).count(),
        },
        'recent_errors': accessible_event_logs(user).filter(event_type__icontains='error').order_by('-created_at')[:8],
    }


def export_file_records_csv(queryset):
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(['File Name', 'Property', 'Source', 'Type', 'Status', 'Expected Date', 'Received At', 'Loaded At'])
    for item in queryset:
        writer.writerow([
            item.file_name,
            item.property.name,
            item.source_system.name,
            item.file_type,
            item.status,
            item.expected_for_date,
            item.received_at,
            item.loaded_at,
        ])
    response = HttpResponse(buffer.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="file-records-export.csv"'
    return response
