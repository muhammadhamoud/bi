from django.core.exceptions import ValidationError
from django.db import models

from apps.settings.mappings.models.base import (
    MappingCategoryBase,
    MappingGroupBase,
    SourceMappingBase,
)


class BookingSourceGroup(MappingGroupBase):
    class Meta:
        db_table = 'settings_booking_sources_groups'
        unique_together = ('property', 'code')
        ordering = ['property__name', 'sort_order', 'name']
        verbose_name = 'Booking Source group'
        verbose_name_plural = 'Booking Source groups'


class BookingSourceCategory(MappingCategoryBase):
    group = models.ForeignKey(
        BookingSourceGroup,
        on_delete=models.CASCADE,
        related_name='categories',
    )

    class Meta:
        db_table = 'settings_booking_sources_categories'
        unique_together = ('property', 'code')
        ordering = ['property__name', 'group__sort_order', 'sort_order', 'name']
        verbose_name = 'Booking Source category'
        verbose_name_plural = 'Booking Source categories'

    def clean(self):
        super().clean()
        if self.group and self.group.property_id != self.property_id:
            raise ValidationError({
                'group': 'Booking source group must belong to the same property.'
            })


class BookingSourceMapping(MappingGroupBase):
    category = models.ForeignKey(
        BookingSourceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mappings',
    )

    class Meta:
        db_table = 'settings_booking_sources_mappings'
        unique_together = ('property', 'code')
        ordering = [
            'property__name',
            'category__group__sort_order',
            'category__sort_order',
            'sort_order',
            'name',
        ]
        verbose_name = 'Booking Source mapping'
        verbose_name_plural = 'Booking Source mappings'

    def clean(self):
        super().clean()
        errors = {}

        if self.category and self.category.property_id != self.property_id:
            errors['category'] = 'Booking source category must belong to the same property.'

        if errors:
            raise ValidationError(errors)

    @property
    def group(self):
        return self.category.group if self.category_id else None


class BookingSourceDetail(SourceMappingBase):
    mapping = models.ForeignKey(
        BookingSourceMapping,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='details',
    )

    class Meta:
        db_table = 'settings_booking_source_details'
        unique_together = ('property', 'code')
        ordering = ['property__name', 'mapping__sort_order', 'sort_order', 'code']
        verbose_name = 'Booking Source detail'
        verbose_name_plural = 'Booking Source details'

    def clean(self):
        super().clean()
        if self.mapping and self.mapping.property_id != self.property_id:
            raise ValidationError({
                'mapping': 'Booking source mapping must belong to the same property.'
            })

    @property
    def group(self):
        return self.mapping.group if self.mapping_id else None

    @property
    def category(self):
        return self.mapping.category if self.mapping_id else None