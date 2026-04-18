from django.core.exceptions import ValidationError
from django.db import models
from apps.settings.mappings.models.base import MappingCategoryBase, MappingGroupBase, SourceMappingBase


class RoomTypeGroup(MappingGroupBase):
    class Meta:
        db_table = 'settings_room_types_groups'
        unique_together = ('property', 'code')
        ordering = ['property__name', 'sort_order', 'name']
        verbose_name = 'Room Type group'
        verbose_name_plural = 'Room Type groups'


class RoomTypeCategory(MappingCategoryBase):
    group = models.ForeignKey(
        RoomTypeGroup,
        on_delete=models.CASCADE,
        related_name='categories',
    )

    class Meta:
        db_table = 'settings_room_types_categories'
        unique_together = ('property', 'code')
        ordering = ['property__name', 'group__sort_order', 'sort_order', 'name']
        verbose_name = 'Room Type category'
        verbose_name_plural = 'Room Type categories'

    def clean(self):
        super().clean()
        if self.group and self.group.property_id != self.property_id:
            raise ValidationError({
                'group': 'Room type group must belong to the same property.'
            })


class RoomTypeMapping(MappingGroupBase):
    category = models.ForeignKey(
        RoomTypeCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mappings',
    )

    class Meta:
        db_table = 'settings_room_types_mappings'
        unique_together = ('property', 'code')
        ordering = [
            'property__name',
            'category__group__sort_order',
            'category__sort_order',
            'sort_order',
            'name',
        ]
        verbose_name = 'Room Type mapping'
        verbose_name_plural = 'Room Type mappings'

    def clean(self):
        super().clean()
        errors = {}

        if self.category and self.category.property_id != self.property_id:
            errors['category'] = 'Room type category must belong to the same property.'

        if errors:
            raise ValidationError(errors)

    @property
    def group(self):
        return self.category.group if self.category_id else None
    

class RoomTypeDetail(SourceMappingBase):
    mapping = models.ForeignKey(
        RoomTypeMapping,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='details',
    )
    number_of_rooms = models.PositiveIntegerField(null=True, blank=True)
    room_class = models.CharField(max_length=120, null=True, blank=True)
    room_category = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        db_table = 'settings_room_type_details'
        unique_together = ('property', 'code')
        ordering = ['property__name', 'mapping__sort_order', 'sort_order', 'code']
        verbose_name = 'Room Type detail'
        verbose_name_plural = 'Room Type details'

    def clean(self):
        super().clean()
        if self.mapping and self.mapping.property_id != self.property_id:
            raise ValidationError({
                'mapping': 'Room type must belong to the same property.'
            })

    @property
    def group(self):
        return self.mapping.group if self.mapping_id else None

    @property
    def category(self):
        return self.mapping.category if self.mapping_id else None
