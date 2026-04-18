from django.conf import settings
from django.db import models
from django.urls import reverse

from apps.core.common.models import ActivatableModel, AuditUserModel, NamedSlugModel, SortableModel, TimeStampedModel


class ReportGroup(NamedSlugModel, SortableModel):
    icon = models.CharField(max_length=40, blank=True)
    color = models.CharField(max_length=100, blank=True, null=True)
    category = models.CharField(max_length=80, blank=True)
    visibility_flags = models.CharField(max_length=255, blank=True)
    properties = models.ManyToManyField('propertycore.Property', through='PropertyReportGroupSubscription', related_name='report_groups')

    class Meta:
        db_table = 'powerbi_report_groups'
        ordering = ['sort_order', 'name']

    def get_absolute_url(self):
        return reverse('powerbi:group-detail', kwargs={'slug': self.slug})


class PropertyReportGroupSubscription(TimeStampedModel, ActivatableModel):
    property = models.ForeignKey('propertycore.Property', on_delete=models.CASCADE, related_name='report_group_subscriptions')
    report_group = models.ForeignKey(ReportGroup, on_delete=models.CASCADE, related_name='property_subscriptions')
    starts_on = models.DateField(null=True, blank=True)
    ends_on = models.DateField(null=True, blank=True)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'powerbi_property_report_group_subscriptions'
        unique_together = ('property', 'report_group')

    def __str__(self):
        return f'{self.property.name} / {self.report_group.name}'


class PowerBIReport(TimeStampedModel, ActivatableModel, AuditUserModel, SortableModel):
    report_group = models.ForeignKey(ReportGroup, on_delete=models.CASCADE, related_name='reports')
    name = models.CharField(max_length=140)
    slug = models.SlugField(max_length=160, unique=True)
    description = models.TextField(blank=True)
    powerbi_report_id = models.CharField(max_length=120)
    workspace_id = models.CharField(max_length=120)
    dataset_id = models.CharField(max_length=120, blank=True)
    embed_url = models.URLField()
    thumbnail_url = models.URLField(blank=True)
    allowed_roles = models.CharField(max_length=255, blank=True, help_text='Comma separated role names')
    feature_flag = models.CharField(max_length=80, blank=True)
    last_synced_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'powerbi_reports'
        ordering = ['report_group__sort_order', 'sort_order', 'name']

    @property
    def allowed_role_list(self):
        return [role.strip() for role in self.allowed_roles.split(',') if role.strip()]

    def get_absolute_url(self):
        return reverse('powerbi:report-detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name


class ReportViewAuditLog(TimeStampedModel):
    report = models.ForeignKey(PowerBIReport, on_delete=models.CASCADE, related_name='view_audits')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    property = models.ForeignKey('propertycore.Property', on_delete=models.SET_NULL, null=True, blank=True)
    success = models.BooleanField(default=True)
    detail = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True)

    class Meta:
        db_table = 'powerbi_report_view_audit_logs'
        ordering = ['-created_at']
