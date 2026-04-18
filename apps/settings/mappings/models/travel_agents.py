from django.core.exceptions import ValidationError
from django.db import models

from apps.settings.mappings.models.base import MappingCategoryBase, MappingGroupBase, SourceMappingBase


class TravelAgentGroup(MappingGroupBase):
    class Meta:
        db_table = 'settings_travel_agents_groups'
        unique_together = ('property', 'code')
        ordering = ['property__name', 'sort_order', 'name']
        verbose_name = 'Travel Agent group'
        verbose_name_plural = 'Travel Agent groups'


class TravelAgentCategory(MappingCategoryBase):
    group = models.ForeignKey(
        TravelAgentGroup,
        on_delete=models.CASCADE,
        related_name='categories',
    )

    class Meta:
        db_table = 'settings_travel_agents_categories'
        unique_together = ('property', 'code')
        ordering = ['property__name', 'group__sort_order', 'sort_order', 'name']
        verbose_name = 'Travel Agent category'
        verbose_name_plural = 'Travel Agent categories'

    def clean(self):
        super().clean()
        if self.group and self.group.property_id != self.property_id:
            raise ValidationError({
                'group': 'Travel agent group must belong to the same property.'
            })


class TravelAgentMapping(MappingGroupBase):
    category = models.ForeignKey(
        TravelAgentCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mappings',
    )

    class Meta:
        db_table = 'settings_travel_agents_mappings'
        unique_together = ('property', 'code')
        ordering = [
            'property__name',
            'category__group__sort_order',
            'category__sort_order',
            'sort_order',
            'name',
        ]
        verbose_name = 'Travel Agent mapping'
        verbose_name_plural = 'Travel Agent mappings'

    def clean(self):
        super().clean()
        errors = {}

        if self.category and self.category.property_id != self.property_id:
            errors['category'] = 'Travel agent category must belong to the same property.'

        if errors:
            raise ValidationError(errors)

    @property
    def group(self):
        return self.category.group if self.category_id else None


class TravelAgentDetail(SourceMappingBase):
    mapping = models.ForeignKey(
        TravelAgentMapping,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='details',
    )

    class Meta:
        db_table = 'settings_travel_agent_details'
        unique_together = ('property', 'code')
        ordering = ['property__name', 'mapping__sort_order', 'sort_order', 'code']
        verbose_name = 'Travel Agent detail'
        verbose_name_plural = 'Travel Agent details'

    def clean(self):
        super().clean()
        if self.mapping and self.mapping.property_id != self.property_id:
            raise ValidationError({
                'mapping': 'Travel agent mapping must belong to the same property.'
            })

    @property
    def group(self):
        return self.mapping.group if self.mapping_id else None

    @property
    def category(self):
        return self.mapping.category if self.mapping_id else None