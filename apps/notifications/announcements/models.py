from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.core.common.models import ActivatableModel, AuditUserModel, TimeStampedModel


class AnnouncementQuerySet(models.QuerySet):
    def filter_active(self, now=None):
        now = now or timezone.now()
        return self.filter(is_active=True, is_published=True).filter(
            Q(starts_at__isnull=True) | Q(starts_at__lte=now),
            Q(ends_at__isnull=True) | Q(ends_at__gte=now),
        )


class Announcement(TimeStampedModel, ActivatableModel, AuditUserModel):
    class Level(models.TextChoices):
        INFO = 'info', 'Info'
        WARNING = 'warning', 'Warning'
        CRITICAL = 'critical', 'Critical'

    title = models.CharField(max_length=160)
    body = models.TextField()
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.INFO)
    is_published = models.BooleanField(default=False)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)
    target_roles = models.CharField(max_length=255, blank=True, help_text='Comma separated role names')
    properties = models.ManyToManyField('propertycore.Property', blank=True, related_name='announcements')

    objects = AnnouncementQuerySet.as_manager()

    class Meta:
        db_table = 'announcements'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def target_role_list(self):
        return [role.strip() for role in self.target_roles.split(',') if role.strip()]

    def is_visible_to_user(self, user):
        if not getattr(user, 'is_authenticated', False):
            return False
        if self.target_role_list and not user.groups.filter(name__in=self.target_role_list).exists() and not user.is_superuser:
            return False
        if not self.properties.exists() or user.is_superuser:
            return True
        return user.property_assignments.filter(property__in=self.properties.all(), is_active=True).exists()


class AnnouncementAcknowledgement(TimeStampedModel):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='acknowledgements')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='announcement_acknowledgements')
    read_at = models.DateTimeField(null=True, blank=True)
    dismissed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'announcement_acknowledgements'
        unique_together = ('announcement', 'user')
