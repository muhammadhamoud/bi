from django.core.exceptions import ValidationError
from django.db import models

from apps.settings.mappings.models.base import MappingCategoryBase, MappingGroupBase, SourceMappingBase
from apps.settings.mappings.models.origins import OriginDetail
from apps.settings.mappings.models.segmentations import SegmentDetail


# class RateCodeGroup(MappingGroupBase):
#     class Meta:
#         db_table = 'settings_rate_codes_groups'
#         unique_together = ('property', 'code')
#         ordering = ['property__name', 'sort_order', 'name']
#         verbose_name = 'Rate Code group'
#         verbose_name_plural = 'Rate Code groups'


# class RateCodeCategory(MappingCategoryBase):
#     group = models.ForeignKey(
#         RateCodeGroup,
#         on_delete=models.CASCADE,
#         related_name='categories',
#     )

#     class Meta:
#         db_table = 'settings_rate_codes_categories'
#         unique_together = ('property', 'code')
#         ordering = ['property__name', 'group__sort_order', 'sort_order', 'name']
#         verbose_name = 'Rate Code category'
#         verbose_name_plural = 'Rate Code categories'

#     def clean(self):
#         super().clean()
#         if self.group and self.group.property_id != self.property_id:
#             raise ValidationError({
#                 'group': 'Rate code group must belong to the same property.'
#             })


# class RateCodeMapping(MappingGroupBase):
#     category = models.ForeignKey(
#         SegmentDetail,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='rate_code_mappings',
#     )

#     class Meta:
#         db_table = 'settings_rate_codes_mappings'
#         unique_together = ('property', 'code')
#         ordering = [
#             'property__name',
#             'category__sort_order',
#             'sort_order',
#             'name',
#         ]
#         verbose_name = 'Rate Code mapping'
#         verbose_name_plural = 'Rate Code mappings'

#     def clean(self):
#         super().clean()
#         errors = {}

#         if self.category and self.category.property_id != self.property_id:
#             errors['category'] = 'Category detail must belong to the same property.'

#         if errors:
#             raise ValidationError(errors)

#     @property
#     def group(self):
#         return self.category.group if self.category_id else None

#     @property
#     def category_c(self):
#         return self.category.category if self.category_id else None



class RateCodeDetail(SourceMappingBase):
    mapping = models.ForeignKey(
        SegmentDetail,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rate_code_details',
    )
    origin = models.ForeignKey(
        OriginDetail,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rate_code_details',
    )

    class Meta:
        db_table = 'settings_rate_code_details'
        unique_together = ('property', 'code')
        ordering = [
            'property__name',
            'mapping__sort_order',
            'sort_order',
            'code',
        ]
        verbose_name = 'Rate Code detail'
        verbose_name_plural = 'Rate Code details'

    def clean(self):
        super().clean()
        errors = {}

        if self.mapping and self.mapping.property_id != self.property_id:
            errors['mapping'] = 'Segment detail must belong to the same property.'

        if self.origin and self.origin.property_id != self.property_id:
            errors['origin'] = 'Origin detail must belong to the same property.'

        if errors:
            raise ValidationError(errors)

    @property
    def category(self):
        return self.mapping.category if self.mapping_id else None

    @property
    def group(self):
        return self.mapping.group if self.mapping_id else None
    

