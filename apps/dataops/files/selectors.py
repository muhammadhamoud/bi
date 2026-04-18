from django.db.models import Count
from django.db.models.functions import Coalesce

from apps.core.common.access import filter_queryset_for_user
from apps.dataops.files.models import FileDownloadHistory, FileEventLog, FileRecord


def accessible_file_records(user):
    return filter_queryset_for_user(FileRecord.objects.select_related('property', 'source_system', 'expected_definition'), user)


def accessible_download_history(user):
    return filter_queryset_for_user(FileDownloadHistory.objects.select_related('file_record', 'user', 'property'), user)


def accessible_event_logs(user):
    return filter_queryset_for_user(FileEventLog.objects.select_related('file_record', 'actor_user', 'file_record__property'), user, property_lookup='file_record__property')
