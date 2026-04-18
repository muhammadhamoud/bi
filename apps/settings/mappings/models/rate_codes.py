from django.core.exceptions import ValidationError
from django.db import models

from apps.settings.mappings.models.base import MappingCategoryBase, MappingGroupBase, SourceMappingBase


class RateCodeGroup(MappingGroupBase):
    class Meta:
        db_table = 'settings_rate_codes_groups'
        unique_together = ('property', 'code')
        ordering = ['property__name', 'sort_order', 'name']
        verbose_name = 'Rate Code group'
        verbose_name_plural = 'Rate Code groups'


class RateCodeCategory(MappingCategoryBase):
    group = models.ForeignKey(
        RateCodeGroup,
        on_delete=models.CASCADE,
        related_name='categories',
    )

    class Meta:
        db_table = 'settings_rate_codes_categories'
        unique_together = ('property', 'code')
        ordering = ['property__name', 'group__sort_order', 'sort_order', 'name']
        verbose_name = 'Rate Code category'
        verbose_name_plural = 'Rate Code categories'

    def clean(self):
        super().clean()
        if self.group and self.group.property_id != self.property_id:
            raise ValidationError({
                'group': 'Rate code group must belong to the same property.'
            })


class RateCodeMapping(MappingGroupBase):
    category = models.ForeignKey(
        RateCodeCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mappings',
    )

    class Meta:
        db_table = 'settings_rate_codes_mappings'
        unique_together = ('property', 'code')
        ordering = [
            'property__name',
            'category__group__sort_order',
            'category__sort_order',
            'sort_order',
            'name',
        ]
        verbose_name = 'Rate Code mapping'
        verbose_name_plural = 'Rate Code mappings'

    def clean(self):
        super().clean()
        errors = {}

        if self.category and self.category.property_id != self.property_id:
            errors['category'] = 'Rate code category must belong to the same property.'

        if errors:
            raise ValidationError(errors)

    @property
    def group(self):
        return self.category.group if self.category_id else None


class RateCodeDetail(SourceMappingBase):
    mapping = models.ForeignKey(
        RateCodeMapping,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='details',
    )
    
    class Meta:
        db_table = 'settings_rate_code_details'
        unique_together = ('property', 'code')
        ordering = ['property__name', 'mapping__sort_order', 'sort_order', 'code']
        verbose_name = 'Rate Code detail'
        verbose_name_plural = 'Rate Code details'

    def clean(self):
        super().clean()
        if self.mapping and self.mapping.property_id != self.property_id:
            raise ValidationError({
                'mapping': 'Rate code mapping must belong to the same property.'
            })

    @property
    def group(self):
        return self.mapping.group if self.mapping_id else None

    @property
    def category(self):
        return self.mapping.category if self.mapping_id else None