from django.conf import settings
from django.db import models

from apps.core.common.models import TimeStampedModel


class SecurityEvent(TimeStampedModel):
    class Severity(models.TextChoices):
        INFO = 'info', 'Info'
        WARNING = 'warning', 'Warning'
        ERROR = 'error', 'Error'

    category = models.CharField(max_length=80)
    event_type = models.CharField(max_length=120)
    severity = models.CharField(max_length=20, choices=Severity.choices, default=Severity.INFO)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    property = models.ForeignKey('propertycore.Property', on_delete=models.SET_NULL, null=True, blank=True)
    object_repr = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    details = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'security_events'
        ordering = ['-created_at']
        verbose_name = 'Security event'
        verbose_name_plural = 'Security events'

    def __str__(self):
        return f'{self.category}:{self.event_type}'
