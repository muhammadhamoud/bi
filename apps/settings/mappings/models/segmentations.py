from django.core.exceptions import ValidationError
from django.db import models
from apps.settings.mappings.models.base import MappingGroupBase, SourceMappingBase


class SegmentGroup(MappingGroupBase):
    class Meta:
        db_table = 'settings_segment_groups'
        unique_together = ('property', 'code')
        ordering = ['property__name', 'sort_order', 'name']


class SegmentCategory(MappingGroupBase):
    group = models.ForeignKey(SegmentGroup, on_delete=models.CASCADE, related_name='categories')

    class Meta:
        db_table = 'settings_segment_categories'
        unique_together = ('property', 'code')
        ordering = ['property__name', 'group__sort_order', 'sort_order', 'name']

    def clean(self):
        super().clean()
        if self.group and self.group.property_id != self.property_id:
            raise ValidationError({'group': 'Segment group must belong to the same property.'})


class SegmentMapping(MappingGroupBase):
    category = models.ForeignKey(SegmentCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='segments')

    class Meta:
        db_table = 'settings_segments'
        unique_together = ('property', 'code')
        ordering = ['property__name', 'category__group__sort_order', 'category__sort_order', 'sort_order', 'name']

    def clean(self):
        super().clean()
        errors = {}

        if self.category and self.category.property_id != self.property_id:
            errors['category'] = 'Segment category must belong to the same property.'

        if errors:
            raise ValidationError(errors)

    @property
    def group(self):
        return self.category.group if self.category_id else None



class SegmentDetail(SourceMappingBase):
    mapping = models.ForeignKey(
        SegmentMapping,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='details',
    )

    class Meta:
        db_table = 'settings_segment_details'
        unique_together = ('property', 'code')
        ordering = ['property__name', 'mapping__sort_order', 'sort_order', 'code']

    def clean(self):
        super().clean()
        if self.mapping and self.mapping.property_id != self.property_id:
            raise ValidationError({'mapping': 'Mapping must belong to the same property.'})

    @property
    def group(self):
        return self.mapping.group if self.mapping_id else None

    @property
    def category(self):
        return self.mapping.category if self.mapping_id else None

