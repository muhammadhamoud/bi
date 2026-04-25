from datetime import date, datetime
from zoneinfo import ZoneInfo

from django.utils import timezone

from apps.roi_ingestion.constants import DUBAI_TIMEZONE


def dubai_today() -> date:
    return timezone.now().astimezone(ZoneInfo(DUBAI_TIMEZONE)).date()


def parse_iso_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value[:10])


def parse_compact_date(value: str) -> date:
    return datetime.strptime(value, "%Y%m%d").date()


def format_compact_date(value: date) -> str:
    return value.strftime("%Y%m%d")
