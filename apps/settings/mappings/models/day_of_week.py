from django.core.exceptions import ValidationError
from django.db import models

from apps.settings.mappings.models.base import MappingGroupBase, SourceMappingBase


class DayOfWeekGroup(MappingGroupBase):
    class Meta:
        db_table = 'settings_day_of_week_groups'
        unique_together = ('property', 'code')
        ordering = ['property__name', 'sort_order', 'name']
        verbose_name = 'Day of Week group'
        verbose_name_plural = 'Day of Week groups'


class DayOfWeekMapping(SourceMappingBase):
    group = models.ForeignKey(DayOfWeekGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='mappings')

    class Meta:
        db_table = 'settings_day_of_week_mappings'
        unique_together = ('property', 'code')
        ordering = ['property__name', 'sort_order', 'code']
        verbose_name = 'Day of Week mapping'
        verbose_name_plural = 'Day of Week mappings'

    def clean(self):
        super().clean()
        if self.group and self.group.property_id != self.property_id:
            raise ValidationError({'group': 'Selected group must belong to the same property.'})
