from django.core.exceptions import ValidationError
from django.db import models

from apps.settings.mappings.models.base import MappingCategoryBase, MappingGroupBase, SourceMappingBase


class GuestCountryGroup(MappingGroupBase):
    class Meta:
        db_table = 'settings_guest_countries_groups'
        unique_together = ('property', 'code')
        ordering = ['property__name', 'sort_order', 'name']
        verbose_name = 'Guest Country group'
        verbose_name_plural = 'Guest Country groups'


class GuestCountryCategory(MappingCategoryBase):
    group = models.ForeignKey(
        GuestCountryGroup,
        on_delete=models.CASCADE,
        related_name='categories',
    )

    class Meta:
        db_table = 'settings_guest_countries_categories'
        unique_together = ('property', 'code')
        ordering = ['property__name', 'group__sort_order', 'sort_order', 'name']
        verbose_name = 'Guest Country category'
        verbose_name_plural = 'Guest Country categories'

    def clean(self):
        super().clean()
        if self.group and self.group.property_id != self.property_id:
            raise ValidationError({
                'group': 'Guest country group must belong to the same property.'
            })


class GuestCountryMapping(MappingGroupBase):
    category = models.ForeignKey(
        GuestCountryCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mappings',
    )

    class Meta:
        db_table = 'settings_guest_countries_mappings'
        unique_together = ('property', 'code')
        ordering = [
            'property__name',
            'category__group__sort_order',
            'category__sort_order',
            'sort_order',
            'name',
        ]
        verbose_name = 'Guest Country mapping'
        verbose_name_plural = 'Guest Country mappings'

    def clean(self):
        super().clean()
        errors = {}

        if self.category and self.category.property_id != self.property_id:
            errors['category'] = 'Guest country category must belong to the same property.'

        if errors:
            raise ValidationError(errors)

    @property
    def group(self):
        return self.category.group if self.category_id else None


class GuestCountryDetail(SourceMappingBase):
    mapping = models.ForeignKey(
        GuestCountryMapping,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='details',
    )

    class Meta:
        db_table = 'settings_guest_country_details'
        unique_together = ('property', 'code')
        ordering = ['property__name', 'mapping__sort_order', 'sort_order', 'code']
        verbose_name = 'Guest Country detail'
        verbose_name_plural = 'Guest Country details'

    def clean(self):
        super().clean()
        if self.mapping and self.mapping.property_id != self.property_id:
            raise ValidationError({
                'mapping': 'Guest country mapping must belong to the same property.'
            })

    @property
    def group(self):
        return self.mapping.group if self.mapping_id else None

    @property
    def category(self):
        return self.mapping.category if self.mapping_id else None