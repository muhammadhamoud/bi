from django.core.exceptions import ValidationError
from django.db import models

from apps.settings.mappings.models.base import MappingCategoryBase, MappingGroupBase, SourceMappingBase


class PackageGroup(MappingGroupBase):
    class Meta:
        db_table = 'settings_packages_groups'
        unique_together = ('property', 'code')
        ordering = ['property__name', 'sort_order', 'name']
        verbose_name = 'Package group'
        verbose_name_plural = 'Package groups'


class PackageCategory(MappingCategoryBase):
    group = models.ForeignKey(
        PackageGroup,
        on_delete=models.CASCADE,
        related_name='categories',
    )

    class Meta:
        db_table = 'settings_packages_categories'
        unique_together = ('property', 'code')
        ordering = ['property__name', 'group__sort_order', 'sort_order', 'name']
        verbose_name = 'Package category'
        verbose_name_plural = 'Package categories'

    def clean(self):
        super().clean()
        if self.group and self.group.property_id != self.property_id:
            raise ValidationError({
                'group': 'Package group must belong to the same property.'
            })


class PackageMapping(MappingGroupBase):
    category = models.ForeignKey(
        PackageCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mappings',
    )

    class Meta:
        db_table = 'settings_packages_mappings'
        unique_together = ('property', 'code')
        ordering = [
            'property__name',
            'category__group__sort_order',
            'category__sort_order',
            'sort_order',
            'name',
        ]
        verbose_name = 'Package mapping'
        verbose_name_plural = 'Package mappings'

    def clean(self):
        super().clean()
        errors = {}

        if self.category and self.category.property_id != self.property_id:
            errors['category'] = 'Package category must belong to the same property.'

        if errors:
            raise ValidationError(errors)

    @property
    def group(self):
        return self.category.group if self.category_id else None


class PackageDetail(SourceMappingBase):
    mapping = models.ForeignKey(
        PackageMapping,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='details',
    )

    class Meta:
        db_table = 'settings_package_details'
        unique_together = ('property', 'code')
        ordering = ['property__name', 'mapping__sort_order', 'sort_order', 'code']
        verbose_name = 'Package detail'
        verbose_name_plural = 'Package details'

    def clean(self):
        super().clean()
        if self.mapping and self.mapping.property_id != self.property_id:
            raise ValidationError({
                'mapping': 'Package mapping must belong to the same property.'
            })

    @property
    def group(self):
        return self.mapping.group if self.mapping_id else None

    @property
    def category(self):
        return self.mapping.category if self.mapping_id else None